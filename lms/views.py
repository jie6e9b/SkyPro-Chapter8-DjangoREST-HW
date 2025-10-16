from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from lms.models import Course, Lesson, CourseSubscription, Payment
from lms.serializers import (
    CourseSerializer,
    LessonSerializer,
    CourseSubscriptionSerializer,
    PaymentSerializer,
    CreatePaymentSerializer,
    PaymentStatusSerializer,
)
from lms.paginators import CoursePaginator, LessonPaginator
from users.permissions import IsModerator, IsOwner
from lms.stripe_services import StripeService


# =====================================================
# COURSE VIEWSET
# =====================================================

class CourseViewSet(viewsets.ModelViewSet):
    """Управление курсами"""

    queryset = Course.objects.all().order_by("id")
    serializer_class = CourseSerializer
    pagination_class = CoursePaginator

    def get_permissions(self):
        action_permissions = {
            "create": [IsAuthenticated, ~IsModerator],
            "update": [IsAuthenticated, IsModerator | IsOwner],
            "partial_update": [IsAuthenticated, IsModerator | IsOwner],
            "retrieve": [IsAuthenticated, IsModerator | IsOwner],
            "destroy": [IsAuthenticated, ~IsModerator & IsOwner],
            "list": [IsAuthenticated],
        }
        self.permission_classes = action_permissions.get(self.action, [IsAuthenticated])
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == "list" and not self.request.user.groups.filter(name="Moderators").exists():
            qs = qs.filter(owner=self.request.user)
        return qs


# =====================================================
# LESSON VIEWSET
# =====================================================

class LessonViewSet(viewsets.ModelViewSet):
    """Управление уроками"""

    queryset = Lesson.objects.all().order_by("id")
    serializer_class = LessonSerializer
    pagination_class = LessonPaginator

    def get_permissions(self):
        action_permissions = {
            "create": [IsAuthenticated, ~IsModerator],
            "update": [IsAuthenticated, IsModerator | IsOwner],
            "partial_update": [IsAuthenticated, IsModerator | IsOwner],
            "retrieve": [IsAuthenticated, IsModerator | IsOwner],
            "destroy": [IsAuthenticated, ~IsModerator & IsOwner],
            "list": [IsAuthenticated],
        }
        self.permission_classes = action_permissions.get(self.action, [IsAuthenticated])
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == "list" and not self.request.user.groups.filter(name="Moderators").exists():
            qs = qs.filter(owner=self.request.user)
        return qs


# =====================================================
# COURSE SUBSCRIPTION (FUNCTION-BASED VIEWS)
# =====================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def subscribe_to_course(request, course_id: int):
    """Подписка пользователя на курс"""
    course = get_object_or_404(Course, id=course_id)

    if CourseSubscription.objects.filter(user=request.user, course=course).exists():
        return Response({"detail": "Вы уже подписаны на этот курс"}, status=status.HTTP_400_BAD_REQUEST)

    subscription = CourseSubscription.objects.create(user=request.user, course=course)
    serializer = CourseSubscriptionSerializer(subscription)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def unsubscribe_from_course(request, course_id: int):
    """Отписка пользователя от курса"""
    subscription = CourseSubscription.objects.filter(user=request.user, course_id=course_id).first()
    if not subscription:
        return Response({"detail": "Подписка не найдена"}, status=status.HTTP_404_NOT_FOUND)

    subscription.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================
# COURSE SUBSCRIPTION (CLASS-BASED VIEW)
# =====================================================

class CourseSubscriptionView(APIView):
    """Добавление или удаление подписки на курс"""

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        course_id = request.data.get("course")
        course = get_object_or_404(Course, id=course_id)

        existing = CourseSubscription.objects.filter(user=request.user, course=course)

        if existing.exists():
            existing.delete()
            message = "Подписка удалена"
        else:
            CourseSubscription.objects.create(user=request.user, course=course)
            message = "Подписка добавлена"

        return Response({"message": message})


# =====================================================
# PAYMENT SUCCESS / CANCEL TEMPLATES
# =====================================================

class PaymentSuccessView(LoginRequiredMixin, TemplateView):
    template_name = "lms/payment_success.html"


class PaymentCancelView(LoginRequiredMixin, TemplateView):
    template_name = "lms/payment_cancel.html"


# =====================================================
# PAYMENT VIEWSET
# =====================================================

class PaymentViewSet(viewsets.ModelViewSet):
    """CRUD и операции с платежами через Stripe"""

    queryset = Payment.objects.select_related("user", "course", "lesson").all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ["course", "lesson", "user"]
    ordering_fields = ["payment_date"]
    search_fields = ["user__username", "user__email"]

    def get_serializer_class(self):
        if self.action == "create_payment":
            return CreatePaymentSerializer
        if self.action == "check_status":
            return PaymentStatusSerializer
        return PaymentSerializer

    @action(detail=False, methods=["post"])
    def create_payment(self, request):
        """Создание платежа через Stripe"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course = serializer.validated_data.get("course")
        lesson = serializer.validated_data.get("lesson")

        if not course and not lesson:
            return Response({"error": "Необходимо указать курс или урок"}, status=status.HTTP_400_BAD_REQUEST)

        item = course or lesson
        amount = getattr(item, "price", 0)

        try:
            payment = Payment.objects.create(
                user=request.user,
                course=course,
                lesson=lesson,
                payment_price=amount,
                payment_status="pending",
            )

            stripe_service = StripeService()
            description = f"Курс: {course.name}" if course else f"Урок: {lesson.name}"

            product = stripe_service.create_product(name=item.name, description=description)
            payment.stripe_product_id = product.id

            price = stripe_service.create_price(product_id=product.id, price=int(amount))

            session_id, payment_url = stripe_service.create_session(
                price_id=price.id,
                success_url=request.build_absolute_uri("/payment/success/"),
                cancel_url=request.build_absolute_uri("/payment/cancel/"),
                customer_email=request.user.email,
            )

            payment.stripe_payment_id = session_id
            payment.stripe_payment_url = payment_url
            payment.save()

            return Response(
                {"id": payment.id, "payment_url": payment_url, "status": payment.payment_status},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def check_status(self, request, pk=None):
        """Проверка статуса платежа"""
        payment = self.get_object()
        stripe_service = StripeService()

        try:
            new_status = stripe_service.get_payment_status(payment.stripe_payment_id)

            if new_status != payment.payment_status:
                payment.payment_status = new_status
                payment.save()

            serializer = self.get_serializer(payment)
            return Response(serializer.data)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


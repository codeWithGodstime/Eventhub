import logging
from rest_framework import permissions
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework_simplejwt.views import TokenObtainPairView as SimpleJWTTokenObtainPairView
from django.conf import settings
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

from .models import Notification, NotificationPreference, UserSubscription, SubscriptionPlan
from .serializers import UserSerializer, TokenObtainSerializer

logger = logging.getLogger(__name__)

User = get_user_model()

class UserViewset(viewsets.ModelViewSet):
    serializer_class = UserSerializer.UserRetrieveSerializer
    queryset = User.objects.all()

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        serializer = UserSerializer.UserCreateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()

            response_serializer = UserSerializer.UserRetrieveSerializer(user)

            refresh = RefreshToken.for_user(user)
            access = refresh.access_token

            # Attach tokens to the serializer instance
            data = {
                "refresh": str(refresh),
                "access": str(access),
                "user": response_serializer.data
            }

            response = Response(data=data, status=status.HTTP_201_CREATED)
            return response
        else:
            logger.error(f"User registration failed due to invalid data: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def me(self, request, *args, **kwargs):
        user = request.user
        profile = user.profile
        serializer = UserSerializer.UserRetrieveSerializer(profile)
        return Response(data=serializer.data)
    
    @action(methods=['get'], detail=True, permission_classes=[permissions.IsAuthenticated])
    def public(self, request, *args, **kwargs):
        """ viewing anther user profile """
        user = self.get_object()
        user = user.profile
        
        serializer = UserSerializer.ProfileSerializer(user)
        return Response(data=serializer.data)
    

    @action(methods=["post"], detail=False, permission_classes=[permissions.AllowAny])
    def reset_password(self, request, *args, **kwargs):
        logger.info(f"Password reset request with data: {request.data}")

        serializer = UserSerializer.ResetPasswordRequestSerializer(
            data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = request.data["email"]
            user = User.objects.filter(email__iexact=email).first()

            if user:
                logger.info(f"User found for email: {email}, initiating password reset.")
                token_generator = PasswordResetTokenGenerator()
                token = token_generator.make_token(user)
                logger.debug(f"Generated token: {token}")

                reset_url = f"{settings.PASSWORD_RESET_BASE_URL}/{user.id}:{token}"
                logger.info(f"Password reset URL: {reset_url}")

                subject = "Password Reset Request"
                message = f"Hi {user.first_name},\n\nPlease click the link below to reset your \npassword:{reset_url}\n\nIf you did not request this, please ignore this email."
                email_from = settings.DEFAULT_FROM_EMAIL

                logger.info(f"Sending password reset email to: {email}")
                user.email_user(subject, message, email_from)
                logger.info(f"Password reset email sent successfully to: {email}")

                return Response({'message': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)
            else:
                logger.warning(f"User with email {email} not found.")
                return Response({"error": "User with email not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            logger.error(f"Password reset request failed due to invalid data: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["post"], detail=False, permission_classes=[permissions.AllowAny])
    def reset_password_complete(self, request, *args, **kwargs):
        logger.info(f"Password reset complete request with data: {request.data}")

        serializer = UserSerializer.ResetPasswordComplete(data=request.data)
        if serializer.is_valid():
            logger.info("Password reset request completed successfully.")
            serializer.save()
            logger.info(f"Password reset successfully for user: {self.request.user.id}")
            return Response({"message": "Password updated successfully."}, status=status.HTTP_200_OK)
        else:
            logger.error(f"Password reset request failed due to invalid data: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["post"], detail=False, permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request, *args, **kwargs):

        serializer = UserSerializer.ChangePasswordSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            logger.info(f"Password change request with data: {request.data}")
            serializer.save()
            return Response({"message": "Password change successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=['get'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def notification_preferences(self, request, *args, **kwargs):
        """"""
        user = request.user
        preferences, _ = NotificationPreference.objects.get_or_create(user=user)
        serializer = UserSerializer.NotificationPreferenceSerializer(preferences)
        return Response(data=serializer.data, status=200)

    @action(methods=['get'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def update_notification_preferences(self, request, *args, **kwargs):
        """"""
        user = request.user
        request['user'] = user.id
        serializer = UserSerializer.NotificationPreferenceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        preferences, _ = NotificationPreference.objects.update_or_create(data=request.data, partial=True)
        updated_serializer = UserSerializer.NotificationPreferenceSerializer(preferences)

        return Response(data=updated_serializer.data, status=200)

    @action(methods=['POST'], permission_classes=[permissions.IsAuthenticated])
    def notifications(self, request, *args, **kwargs):
        user = request.user

        notifications = user.notification_receiver.all()
        serializer = UserSerializer.NotificationSerializer(notifications, many=True)
        return Response(data=serializer.data)

    @action(methods=['POST'], permission_classes=[permissions.IsAuthenticated])
    def mark_all_notifications_read(self, request, *args, **kwargs):
        user = request.user

        notifications = user.notification_receiver.filter(is_read=False).update(is_read=True)
        serializer = UserSerializer.NotificationSerializer(notifications, many=True)
        return Response(data=serializer.data)

    @action(methods=['POST'], permission_classes=[permissions.IsAuthenticated])
    def mark_notification_read(self, request, *args, **kwargs):
        user = request.user

        serializer = UserSerializer.ReadNotificationSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        notification = user.notification_receiver.filter(id=request.data['id']).update(is_read=True)
        serializer = UserSerializer.NotificationSerializer(notification)
        return Response(data=serializer.data)


class UserSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = UserSubscription.objects.all()
    serializer_class = UserSerializer.UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def view_subscription(self, request):
        """
        View the current subscription details of the logged-in user
        """
        user_subscription = self.get_queryset().first()
        if user_subscription:
            serializer = self.get_serializer(user_subscription)
            return Response(serializer.data)
        return Response({"detail": "No subscription found for this user"}, status=404)

    @action(detail=False, methods=['post'])
    def upgrade_subscription(self, request):
        """
        Upgrade the user's subscription to a higher-tier plan
        """
        current_subscription = self.get_queryset().first()

        if not current_subscription:
            return Response({"detail": "No current subscription found."}, status=404)

        new_plan_id = request.data.get('new_plan_id')
        try:
            new_plan = SubscriptionPlan.objects.get(id=new_plan_id)
        except SubscriptionPlan.DoesNotExist:
            return Response({"detail": "The requested plan does not exist."}, status=400)

        if new_plan.price <= current_subscription.subscription_plan.price:
            return Response({"detail": "New plan must be more expensive than the current one."}, status=400)

        current_subscription.subscription_plan = new_plan
        current_subscription.end_date = timezone.now() + timezone.timedelta(days=30)  # Recalculate end date
        current_subscription.save()

        serializer = self.get_serializer(current_subscription)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def downgrade_subscription(self, request):
        """
        Downgrade the user's subscription to a lower-tier plan
        """
        current_subscription = self.get_queryset().first()

        if not current_subscription:
            return Response({"detail": "No current subscription found."}, status=404)

        # Fetch the new plan from the request
        new_plan_id = request.data.get('new_plan_id')
        try:
            new_plan = SubscriptionPlan.objects.get(id=new_plan_id)
        except SubscriptionPlan.DoesNotExist:
            return Response({"detail": "The requested plan does not exist."}, status=400)

        if new_plan.price >= current_subscription.subscription_plan.price:
            return Response({"detail": "New plan must be less expensive than the current one."}, status=400)

        current_subscription.subscription_plan = new_plan
        current_subscription.end_date = timezone.now() + timezone.timedelta(days=30)
        current_subscription.save()

        serializer = self.get_serializer(current_subscription)
        return Response(serializer.data)

class TokenObtainPairView(SimpleJWTTokenObtainPairView):
     serializer_class = TokenObtainSerializer
 
     def post(self, request, *args, **kwargs) -> Response:
         return super().post(request, *args, **kwargs)
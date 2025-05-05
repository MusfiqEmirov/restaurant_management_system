from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from project_apps.staff.models import Staff
from project_apps.staff.serializers import StaffSerializer
from project_apps.core.logging import get_logger

logger = get_logger(__name__)

class StaffView(APIView):
    
    def get(self, request, staff_id=None):
        """Returns the list of staff or a staff detail."""
        if not request.user.is_authenticated:
            logger.error(f"Unauthorized view attempt: Guest")
            return Response(
                {"error": "Authentication is required to view staff."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = request.user
        logger.debug(
            f"Staff request received: {user.email}, ID: {staff_id}"
        )

        if staff_id:
            staff = get_object_or_404(Staff, id=staff_id, is_deleted=False)
            if user.role == "staff" and staff.user != user:
                logger.error(
                    f"Unauthorized staff view: {user.email}, staff ID: {staff_id}"
                )
                return Response(
                    {"error": "You can only view your own information."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer = StaffSerializer(staff)
            logger.info(f"Staff detail returned: ID {staff_id}")
            return Response(serializer.data, status=status.HTTP_200_OK)

        if user.role != "admin":
            if user.role == "staff":
                staff = get_object_or_404(Staff, user=user, is_deleted=False)
                serializer = StaffSerializer(staff)
                logger.info(f"Own staff information returned: {user.email}")
                return Response(serializer.data, status=status.HTTP_200_OK)
            logger.error(
                f"Unauthorized list view: {user.email}, role: {user.role}"
            )
            return Response(
                {"error": "Only admins can view the staff list."},
                status=status.HTTP_403_FORBIDDEN,
            )

        staff_list = Staff.objects.filter(is_deleted=False)
        serializer = StaffSerializer(staff_list, many=True)
        logger.info(f"Staff list returned: count: {staff_list.count()}")
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Creates a new staff member (only admin)."""
        if not request.user.is_authenticated or request.user.role != "admin":
            logger.error(
                f"Unauthorized create attempt: {request.user.email if request.user.is_authenticated else 'Guest'}, "
                f"role: {request.user.role if request.user.is_authenticated else 'None'}"
            )
            return Response(
                {"error": "Only admins can create staff."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = StaffSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            staff = serializer.save()
            logger.info(
                f"Staff created: ID {staff.id}, "
                f"email: {staff.user.email}, created by: {request.user.email}"
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Serializer error: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, staff_id=None):
        """Updates a staff member (only admin)."""
        if not staff_id:
            logger.error("Staff ID not provided.")
            return Response(
                {"error": "Staff ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not request.user.is_authenticated or request.user.role != "admin":
            logger.error(
                f"Unauthorized update attempt: {request.user.email if request.user.is_authenticated else 'Guest'}, "
                f"role: {request.user.role if request.user.is_authenticated else 'None'}"
            )
            return Response(
                {"error": "Only admins can update staff."},
                status=status.HTTP_403_FORBIDDEN,
            )

        staff = get_object_or_404(Staff, id=staff_id, is_deleted=False)
        serializer = StaffSerializer(
            staff, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            logger.info(
                f"Staff updated: ID {staff.id}, "
                f"email: {staff.user.email}, updated by: {request.user.email}"
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        logger.error(f"Serializer error: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, staff_id=None):
        """Deletes a staff member (only admin, actual deletion)."""
        if not staff_id:
            logger.error("Staff ID not provided.")
            return Response(
                {"error": "Staff ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not request.user.is_authenticated or request.user.role != "admin":
            logger.error(
                f"Unauthorized delete attempt: {request.user.email if request.user.is_authenticated else 'Guest'}, "
                f"role: {request.user.role if request.user.is_authenticated else 'None'}"
            )
            return Response(
                {"error": "Only admins can delete staff."},
                status=status.HTTP_403_FORBIDDEN,
            )

        staff = get_object_or_404(Staff, id=staff_id, is_deleted=False)
        staff.delete()
        logger.info(
            f"Staff permanently deleted: ID {staff.id}, "
            f"email: {staff.user.email}, admin: {request.user.email}"
        )
        return Response(
            {"message": "Staff permanently deleted."},
            status=status.HTTP_200_OK,
        )

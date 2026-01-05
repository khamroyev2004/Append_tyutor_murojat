from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
import requests
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import User, Student, Tutor, Group
from .serializer import *

@permission_classes([AllowAny])
class ApiCheckStudent(ListModelMixin, CreateModelMixin, GenericViewSet):
    serializer_class = HemisUniversalSerializer
    queryset = User.objects.all()
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        hemis_id = serializer.validated_data['hemis_id']
        user = User.objects.filter(hemis_id=hemis_id).first()
        if user:
            return Response(
                {
                    "success": True,
                    "user_id": user.id,
                    "role": "student" if user.role == 1 else "tutor",
                    "full_name": user.full_name,
                    "photo": user.photo,
                },
                status=status.HTTP_200_OK
            )
        headers = {
            "Authorization": f"Bearer {settings.HEMIS_API_TOKEN}",
            "Accept": "application/json"
        }
        student_url = "https://student.bsmi.uz/rest/v1/data/student-list"
        r = requests.get(
            student_url,
            headers=headers,
            params={"type": "student", "search": hemis_id},
            timeout=10
        )
        if r.status_code == 200:
            items = r.json().get("data", {}).get("items", [])
            matched_student = next(
                (i for i in items if str(i.get("student_id_number")) == hemis_id),
                None
            )
            if matched_student:
                item = matched_student
                user = User.objects.create(
                    username=item.get("student_id_number"),
                    first_name=item.get("first_name", ""),
                    last_name=item.get("second_name", ""),
                    full_name=item.get("full_name"),
                    hemis_id=hemis_id,
                    role=1,
                    photo=item.get("image_full"),
                    is_active=False
                )
                group = None
                if item.get("group"):
                    group, _ = Group.objects.get_or_create(
                        name=item["group"]["name"]
                    )

                Student.objects.create(user=user, group=group)

                return Response(
                    {
                        "success": True,
                        "user_id": user.id,
                        "role": "student",
                        "group": group.name if group else None,
                        "photo": user.photo,
                    },
                    status=status.HTTP_201_CREATED
                )
        tutor_url = "https://student.bsmi.uz/rest/v1/data/employee-list"
        r = requests.get(
            tutor_url,
            headers=headers,
            params={"type": "employee", "search": hemis_id, "_staff_position": 34},
            timeout=10
        )
        matched_tutor = None
        if r.status_code == 200:
            items = r.json().get("data", {}).get("items", [])
            matched_tutor = next(
                (
                    i for i in items
                    if str(i.get("id")) == hemis_id
                    or str(i.get("employee_id_number")) == hemis_id
                    or str(i.get("login")) == hemis_id
                ),
                None
            )
        if matched_tutor:
            item = matched_tutor
            user = User.objects.create(
                username=item.get("login") or item.get("employee_id_number"),
                first_name=item.get("first_name", ""),
                last_name=item.get("second_name", ""),
                full_name=item.get("full_name"),
                hemis_id=hemis_id,
                role=2,
                photo=item.get("image_full") or item.get("image"),
                is_active=False
            )
            tutor = Tutor.objects.create(user=user)
            hemis_groups = (
                item.get("groups")
                or item.get("groupList")
                or item.get("tutorGroups")
                or []
            )

            for g in hemis_groups:
                name = g.get("name")
                if not name:
                    continue
                group, _ = Group.objects.get_or_create(name=name)
                group.tutor = tutor
                group.save()

            return Response(
                {
                    "success": True,
                    "source": "hemis_tutor",
                    "user_id": user.id,
                    "role": "tutor",
                    "groups": [g.get("name") for g in hemis_groups if g.get("name")]
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {"success": False, "error": "User not found in HEMIS"},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def auth(request):
    serializer = CreatePasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    hemis_id = serializer.validated_data["hemis_id"]
    password = serializer.validated_data["password"]
    try:
        user = User.objects.get(hemis_id=hemis_id)
    except User.DoesNotExist:
        return Response(
            {"success": False, "error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    if not user.password:
        user.set_password(password)
        user.is_active = True
        user.save()
    else:
        if not user.check_password(password):
            return Response(
                {"success": False, "error": "Invalid password"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {"success": False, "error": "User is not active"},
                status=status.HTTP_403_FORBIDDEN
            )

    refresh = RefreshToken.for_user(user)

    response = {
        "success": True,
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user_id": user.id,
        "full_name": user.full_name,
        "photo": user.photo,
        "role": "student" if user.role == 1 else "tutor",
    }

    if user.role == 2:
        tutor = Tutor.objects.filter(user=user).first()

    if user.role == 1:
        student = Student.objects.select_related(
            "group__tutor__user"
        ).filter(user=user).first()

        if student and student.group and student.group.tutor:
            tutor_user = student.group.tutor.user
            response["tutor"] = {
                "user_id": tutor_user.id,
                "full_name": tutor_user.full_name,
                "photo": tutor_user.photo,
            }
        else:
            response["tutor"] = None

    return Response(response, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_groups(request):
    user = request.user
    if user.role == 2:
        tutor = Tutor.objects.filter(user=user).first()
        if not tutor:
            return Response([], status=status.HTTP_200_OK)
        groups_qs = Group.objects.filter(tutor=tutor).order_by("id")
        groups = []
        for g in groups_qs:
            students = list(
                Student.objects
                .filter(group=g)
                .select_related("user")
                .values(
                    "user_id",
                    "user__full_name",
                    "user__photo",
                    "user__hemis_id",
                )
            )
            groups.append({
                "group_id": g.id,
                "group_name": g.name,
                "students": students
            })
        return Response(groups, status=status.HTTP_200_OK)
    if user.role == 1:
        students = Student.objects.filter(user=user).first()
        return Response(
            {}
            ,
            status=status.HTTP_200_OK, 
        )
    return Response(
        {"error": "Invalid role"},
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"error": "refresh token majburiy"},
                status=status.HTTP_400_BAD_REQUEST
            )
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(
            {"success": True, "message": "Logout qilindi"},
            status=status.HTTP_200_OK
        )
    except Exception:
        return Response(
            {"error": "Noto‘g‘ri token"},
            status=status.HTTP_400_BAD_REQUEST
        )
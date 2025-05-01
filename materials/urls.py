from materials.apps import MaterialsConfig
from rest_framework import routers
from .views import (
    CourseViewSet,
    LessonCreateAPIView,
    LessonListAPIView,
    LessonRetrieveAPIView,
    LessonUpdateAPIView,
    LessonDestroyAPIView,
)
from django.urls import path


app_name = MaterialsConfig.name


router = routers.DefaultRouter()
# URL-ы для Вьюсета Course
router.register(r"course", CourseViewSet, basename="course")  # URL-ы для Вьюсета

urlpatterns = [
    # URL-ы для Lesson APIView
    path("lesson/create/", LessonCreateAPIView.as_view(), name="lesson-create"),
    path("lesson/list/", LessonListAPIView.as_view(), name="lesson-list"),
    path("lesson/list/<int:pk>/", LessonRetrieveAPIView.as_view(), name="lesson-detail"),
    path("lesson/update/<int:pk>/", LessonUpdateAPIView.as_view(), name="lesson-update"),
    path("lesson/delete/<int:pk>/", LessonDestroyAPIView.as_view(), name="lesson-delete"),
] + router.urls

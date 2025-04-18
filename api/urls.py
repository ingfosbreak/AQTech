from django.urls import path
# from .views import Home
# from api.views.storage_views import StorageListView, StorageDetailView
from api.views import StorageListView, StorageDetailView, StaffUserView, UserUpdateView, UserDetailView, UserListView, StudentCreateView, StudentListView, TeacherCreateView, TeacherListView, SessionView, UserInfoView, VerifyTokenView, CombinedCountView, PieChartStaticView
from api.views.category_view import CategoryCreateView, CategoryListView
from api.views.course_views import CourseCreateView, CourseEnrolledView, CourseListView, CourseDetailView, CoursePriceListView, StudentCourseListView, NewUnitCourseDetailView, NewGetAddTeacherList, NewAddTeacherToCourse, NewRemoveTeacherFromCourse, NewCreateCourseAPIView, NewUnitCourseListView, NewStudentUsernameListView, TimeSlotSelectionView, CreateBatchAttendanceAPIView, AttendanceDetailsList
from api.views.session_views import CourseCategoryEnrollmentView, SessionProgressDetailView, SessionProgressView
from api.views.static_views import AttendanceHeatmapView, AttendanceLogView, CoursePerformanceView, RecentAttendanceView
from api.views.student_views import AddStudentView, StudentStatusUpdateView, UserStudentListView
from api.views.user_views import ProfileView
from api.views.teacher_views import ClassSessionView, CreateUserTeacherView, TeacherAssignmentView, TeacherDetailView, TeacherProfileView, TeacherStatusUpdateView, TeacherUsernameListView, NewCreateTeacherUserView, NewTeacherDetailView
from api.views.student_views import AddStudentView, StudentDetailView, StudentUsernameListView, StudentCertificateListView
from api.views import CreatePaymentIntentView, StripeWebhookAPIView
from api.views.storage_views import StorageChangeImage
from api.views.certificate_views import CerificateListView, AllCertificate
from api.views.attendance_views import AttendanceView, AttendanceModifyView, AttendanceListView, UpdateAttendanceStatus, AttendanceListModifyView
from api.views.payments_views import HandleBeforePaymentView
from api.views.receipt_views import ReceiptDetails, ReceiptListView, MyInvoiceView, MyInvoiceDetailView
# from api.views.user_views import StaffUserView, UserUpdateView

urlpatterns = [
    # path('', Home.as_view()),
    path('storages/', StorageListView.as_view(), name='storage-list'),
    path('storages/<int:pk>/', StorageDetailView.as_view(), name='storage-detail'),
    path('storages/image/<int:pk>', StorageChangeImage.as_view(), name="storage-image"),
    path('user/create/', StaffUserView.as_view(), name='user-create'),
    path('user/update/', UserUpdateView.as_view(), name='user-update'),
    path('user/info/', UserInfoView.as_view(), name="user-info"),
    path('user/verify/', VerifyTokenView.as_view(), name="user-verify"),
    path('user/list/', UserListView.as_view(), name="user-list"),
    path('user/<int:user_id>/', UserDetailView.as_view(), name="user-detail"),
    path('user/students/', UserStudentListView.as_view(), name="user-students"),
    path('students/create/', StudentCreateView.as_view(), name="student-create"),
    path('students/status/<int:pk>/', StudentStatusUpdateView.as_view(), name='update_student_status'),
    path("students/add/<int:user_id>/", AddStudentView.as_view(), name="add-student"),
    path('students/', StudentListView.as_view(), name="student-list"),
    path('studentsreforge/', StudentUsernameListView.as_view(), name="student-list-reforged"),
    path('studentscertificate/', StudentCertificateListView.as_view(), name="student-list-certificate"),
    path('students/<int:pk>', StudentDetailView.as_view(), name="student-detail"),
    path('teachers/create/', CreateUserTeacherView.as_view(), name="teacher-create"),
    path('teachers/', TeacherListView.as_view(), name="teacher-list"),
    path('teachers/<int:teacher_id>/', TeacherDetailView.as_view(), name="teacher-list"),
    path('teachers/status/<int:pk>/', TeacherStatusUpdateView.as_view(), name='teacher-status-update'),
    path('teachersreforge/', TeacherUsernameListView.as_view(), name="teacher-list-reforged"),
    path('sessions/create/', SessionView.as_view(), name="session-create"),
    path("sessions/progress/", SessionProgressView.as_view(), name="session-progress"),
    path("session-detail/", SessionProgressDetailView.as_view(), name="session-detail"),
    path("static/count/", CombinedCountView.as_view(), name="combined-count"),
    path("static/pie/", PieChartStaticView.as_view(), name="pie-count"),
    path('courses/', CourseListView.as_view(), name='course-list'),  # GET /courses/
    path('courses-price/', CoursePriceListView.as_view(), name='course-list-price'),  # GET /courses/
    path('course/<int:pk>', CourseDetailView.as_view(), name="course-detail"),
    path('courses/create/', CourseCreateView.as_view(), name='course-create'),  # POST /courses/create/
    path("courses/enrolled/", StudentCourseListView.as_view(), name="completed-courses"),
    path('course-performance/', CoursePerformanceView.as_view(), name='course-performance'),
    path('enrolled-courses/', CourseEnrolledView.as_view(), name='enrolled-course'),  # URL for fetching course details
    path("profile/", ProfileView.as_view(), name="profile"),
    path("certificates-upload/", CerificateListView.as_view(), name="certificate-upload"),
    path("certificates-all/<int:pk>", AllCertificate.as_view(), name="certificate-upload"),
    path('create-payment-intent/', CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    path("webhook/stripe/", StripeWebhookAPIView.as_view(), name="stripe-webhook"),
    path("handle-timeline/", HandleBeforePaymentView.as_view(), name="handle-validation"),
    path("attendance-create/", AttendanceView.as_view(), name="attendance-create"),
    path("attendance-all/", AttendanceModifyView.as_view(), name="attendance-modify"),
    path("attendance-heatmap/", AttendanceHeatmapView.as_view(), name="attendance-heatmap"),
    path("attendance-log/", AttendanceLogView.as_view(), name="attendance-log"),
    path("attendance-update/", UpdateAttendanceStatus.as_view(), name="attendance-update"),
    path("attendance-recent/", RecentAttendanceView.as_view(), name="attendance-recent"),
    path("attendacne-buy/", AttendanceListView.as_view(), name="attendance-buy"),
    path("attendacne-but-modify/", AttendanceListModifyView.as_view(), name="attendance-buy-modify"),
    path('course-enrollment/', CourseCategoryEnrollmentView.as_view(), name='api_course_sessions_grouped_by_type'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/create/', CategoryCreateView.as_view(), name='category-create'),  # POST to create a category
    path('teacher/class/<int:class_id>/sessions/', ClassSessionView.as_view(), name='class-sessions'),


    ## new api ink and kevin
    path('new/teachers/create/', NewCreateTeacherUserView.as_view(), name="new-teacher-create"),
    path('new/teachers/detail/<int:id>/', NewTeacherDetailView.as_view(), name="new-teacher-detail"),
    path('teacher-profile/', TeacherProfileView.as_view(), name='teacher-profile'),
    path('teacher-assignment/', TeacherAssignmentView.as_view(), name='teacher-assignment'),
    path('new/courses/detail/<int:id>/', NewUnitCourseDetailView.as_view(), name="new-unit-course-detail"),
    path('new/courses/add-teacher-list/<int:course_id>/', NewGetAddTeacherList.as_view(), name="new-add-teacher-list"),
    path('new/courses/<int:course_id>/assign-teacher/', NewAddTeacherToCourse.as_view(), name="new-add-teacher"),
    path('new/courses/<int:course_id>/<int:teacher_id>/remove-teacher/', NewRemoveTeacherFromCourse.as_view(), name="new-remove-teacher"),
    path('new/courses/create/', NewCreateCourseAPIView.as_view(), name="new-create-course"),
    path('new/courses/enroll-list/', NewUnitCourseListView.as_view(), name="new-courses-list"),
    path('new/courses/student-enroll/', NewStudentUsernameListView.as_view(), name="new-students-list"),
    path('new/courses/timeslot-selection/', TimeSlotSelectionView.as_view(), name="new-time-selection"),
    path('new/courses/create-batch/', CreateBatchAttendanceAPIView.as_view(), name="new-course-batch"),
    path('new/courses/attend-list/', AttendanceDetailsList.as_view(), name="attend-list"),
    path('new/receipts/all/', ReceiptListView.as_view(), name="receipt-all-new"),
    path('new/receipts/<int:receipt_id>', ReceiptDetails.as_view(), name="receipt-detail-mew"),
    path('new/receipts/students/', MyInvoiceView.as_view(), name="new-student-invoice"),
    path('new/receipts/students/<int:receipt_id>', MyInvoiceDetailView.as_view(), name="new-student-invoice-detail")
]
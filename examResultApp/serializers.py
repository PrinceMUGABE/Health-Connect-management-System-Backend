from rest_framework import serializers
from .models import ExamResult
from trainingCandidateApp.serializers import CandidateSerializer
from trainingApp.serializers import TrainingSerializer  # Adjust the import as necessary
from examApp.serializers import ExamSerializer  # Adjust the import as necessary
from userApp.serializers import UserSerializer
from userApp.models import User
from base64 import b64encode, b64decode
from trainingApp.models import Training
from trainingCandidateApp.models import Candidate
from examApp.models import Exam



class UserSerializer(serializers.ModelSerializer):
    picture_data = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'phone', 'role', 'picture_data', 'created_at']

    def get_picture_data(self, obj):
        if obj.picture_data:
            return b64encode(obj.picture_data).decode('utf-8')  # Convert binary to base64 string
        return None
    
    

class TrainingSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    materials = serializers.FileField(required=False)

    class Meta:
        model = Training
        fields = ['id', 'created_by', 'name', 'materials', 'created_at']
        
        
class CandidateSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    training = TrainingSerializer(read_only=True)

    class Meta:
        model = Candidate
        fields = ['id', 'user', 'training', 'first_name', 'last_name', 'status', 'created_at']
        
        

class ExamSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    training = TrainingSerializer(read_only=True)

    class Meta:
        model = Exam
        fields = ['id', 'created_by', 'training', 'total_marks', 'created_at']


class ExamResultSerializer(serializers.ModelSerializer):
    created_by = CandidateSerializer(read_only=True)
    exam = ExamSerializer(read_only=True)

    class Meta:
        model = ExamResult
        fields = ['id', 'created_by', 'exam', 'total_marks', 'status', 'created_at']









class ExamResultDetailSerializer(serializers.ModelSerializer):
    exam_name = serializers.CharField(source='exam.training.name')
    candidate_first_name = serializers.CharField(source='created_by.first_name')
    candidate_last_name = serializers.CharField(source='created_by.last_name')
    user_phone = serializers.CharField(source='created_by.user.phone')
    training_name = serializers.CharField(source='exam.training.name')
    training_materials = serializers.FileField(source='exam.training.materials')

    class Meta:
        model = ExamResult
        fields = ['total_marks', 'status', 'created_at', 'candidate_first_name', 
                  'candidate_last_name', 'user_phone', 'training_name', 'exam_name', 'training_materials']
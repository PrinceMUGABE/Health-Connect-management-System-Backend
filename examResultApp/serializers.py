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

    class Meta:
        model = User
        fields = ['id', 'phone', 'role', 'created_at']



class TrainingSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    materials = serializers.FileField(required=False)

    class Meta:
        model = Training
        fields = ['id', 'created_by', 'name', 'materials', 'created_at']
        




class ExamSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    training = TrainingSerializer(read_only=True)

    class Meta:
        model = Exam
        fields = ['id', 'created_by', 'training', 'total_marks', 'created_at']





        
class CandidateSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    training = TrainingSerializer(read_only=True)

    class Meta:
        model = Candidate
        fields = ['id', 'user', 'training', 'first_name', 'last_name', 'status', 'created_at']
        




class ExamResultSerializer(serializers.ModelSerializer):
    candidate = CandidateSerializer(source='created_by', read_only=True)  # Use created_by for the candidate field
    exam = ExamSerializer(read_only=True)

    class Meta:
        model = ExamResult
        fields = ['id', 'candidate', 'exam', 'total_marks', 'status', 'created_at']

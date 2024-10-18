from rest_framework import serializers
from .models import Exam, Question, Choice
from userApp.models import User
from trainingApp.models import Training

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'role', 'created_at'] 

class TrainingSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    materials = serializers.FileField(required=False)  # Allow for optional file uploads

    class Meta:
        model = Training
        fields = ['id', 'created_by', 'name', 'materials', 'created_at']

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct']

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'marks', 'choices']
        
        

class ExamSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    training = TrainingSerializer(read_only=True)

    class Meta:
        model = Exam
        fields = ['id', 'created_by', 'training', 'total_marks', 'created_at', 'questions']

    def validate(self, data):
        training = data.get('training')
        if not training:
            raise serializers.ValidationError({"error": "Training is required."})

        if Exam.objects.filter(training=training).exists():
            raise serializers.ValidationError({"error": "An exam already exists for this training."})
        
        return data

    
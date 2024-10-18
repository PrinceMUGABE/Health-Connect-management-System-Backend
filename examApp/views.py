from rest_framework import generics, status, serializers
from rest_framework.exceptions import ValidationError  # Use this for custom error handling
from .models import Exam
from .serializers import ExamSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import QuestionSerializer, ChoiceSerializer
from .models import Question
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Exam, Training
import random

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_exam(request):
    # Get the training ID from the request data
    training_id = request.data.get('training')

    # Check if training ID is provided
    if not training_id:
        return Response({"error": "Training is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the training exists
    try:
        training = Training.objects.get(id=training_id)
    except Training.DoesNotExist:
        return Response({"error": "Training does not exist."}, status=status.HTTP_404_NOT_FOUND)

    # Check if an exam already exists for this training
    if Exam.objects.filter(training=training).exists():
        return Response({"error": "An exam already exists for this training."}, status=status.HTTP_400_BAD_REQUEST)

    # Create the exam
    exam = Exam.objects.create(
        training=training,
        created_by=request.user,
        total_marks=request.data.get('total_marks', 0)  # Default to 0 if not provided
    )

    return Response({"message": "Exam created successfully", "exam_id": exam.id}, status=status.HTTP_201_CREATED)
        
        

# Get exam by ID
class GetExamByIdView(generics.RetrieveAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Exam, Question

class GetExamsByTrainingView(APIView):
    def get(self, request, pk=None):  # training_id will be passed in the URL
        try:
            # Retrieve the exam associated with the training ID (pk)
            exam = Exam.objects.get(training_id=pk)  # Fetch the exam by training ID
            questions = list(Question.objects.filter(exam=exam))  # Convert to a list for shuffling

            # Shuffle the questions
            random.shuffle(questions)

            questions_data = []
            for question in questions:
                choices = [
                    {
                        'id': choice.id,
                        'text': choice.text,
                        'is_correct': choice.is_correct,
                    }
                    for choice in question.choices.all()
                ]
                questions_data.append({
                    'id': question.id,
                    'text': question.text,
                    'marks': question.marks,
                    'choices': choices,
                })

            response_data = {
                'exam_id': exam.id,
                'total_marks': exam.total_marks,
                'created_at': exam.created_at,
                'questions': questions_data,
                'training': exam.training.name,
            }

            # Print the response data to the terminal
            print("Response Data:", response_data)

            return Response(response_data, status=status.HTTP_200_OK)

        except Exam.DoesNotExist:
            return Response({'error': f'Exam for training ID {pk} not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error occurred: {e}")
            return Response({'error': 'An error occurred while fetching the exam.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Get exams by user (created by user)
class GetExamsByUserView(generics.ListAPIView):
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Exam.objects.filter(created_by=self.request.user)


from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from .models import Exam, Question, Choice
import json

class AddQuestionView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        exam_id = self.kwargs['exam_id']
        data = json.loads(request.body)

        # Validate that the exam exists
        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            return JsonResponse({'error': 'Exam not found.'}, status=404)

        # Create the question
        question_text = data.get('text', '')
        if not question_text:
            return JsonResponse({'error': 'Question text is required.'}, status=400)

        question = Question.objects.create(exam=exam, text=question_text)

        # Create choices
        choices_data = data.get('choices', [])
        for choice_data in choices_data:
            choice_text = choice_data.get('text', '')
            is_correct = choice_data.get('is_correct', False)
            Choice.objects.create(question=question, text=choice_text, is_correct=is_correct)

        return JsonResponse({'message': 'Question created successfully!'}, status=201)

# Note: Adjustments for AddChoiceView are not necessary for this implementation.


# Add a choice to a question
class AddChoiceView(generics.CreateAPIView):
    serializer_class = ChoiceSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        question_id = self.kwargs['question_id']
        question = Question.objects.get(id=question_id)
        serializer.save(question=question)


# Update an exam
class UpdateExamView(generics.UpdateAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]


# Update a question of an exam
class UpdateQuestionView(generics.UpdateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]


# Delete an exam
class DeleteExamView(generics.DestroyAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]


# Delete a question from an exam
class DeleteQuestionView(generics.DestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]


# View all exams (newly added class to list all exams)
class GetAllExamsView(generics.ListAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]
    
    
    
    
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from .models import Exam, Question
from .serializers import ExamSerializer, QuestionSerializer  # You may keep these if you need them elsewhere

class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()

    def retrieve(self, request, pk=None):
        try:
            exam = self.get_object()  # This will use pk from the URL
            questions = Question.objects.filter(exam=exam)

            # Prepare the response without using serializers
            questions_data = []
            for question in questions:
                choices = [
                    {
                        'id': choice.id,
                        'text': choice.text,
                        'is_correct': choice.is_correct,
                    }
                    for choice in question.choices.all()
                ]
                questions_data.append({
                    'id': question.id,
                    'text': question.text,
                    'marks': question.marks,
                    'choices': choices,
                })

            response_data = {
                'exam_id': exam.id,
                'total_marks': exam.total_marks,
                'created_at': exam.created_at,
                'questions': questions_data,
            }

            # Print the response data to the terminal
            print("Response Data:", response_data)

            return Response(response_data, status=status.HTTP_200_OK)
        except Exam.DoesNotExist:
            return Response({'error': f'Exam with ID {pk} not found.'}, status=status.HTTP_404_NOT_FOUND)

    
    
class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        question = self.get_object()
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

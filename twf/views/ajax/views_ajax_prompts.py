import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from twf.models import Prompt
from twf.views.views_base import TWFView


@csrf_exempt
def save_prompt(request):
    """Saves or updates a prompt."""
    if request.method == "POST":
        data = json.loads(request.body)
        prompt_id = data.get("prompt_id")
        role = data.get("role")
        prompt_text = data.get("prompt")  # Rename to avoid conflict
        project = TWFView.s_get_project(request)

        if prompt_id:
            # Update the prompt
            try:
                prompt = Prompt.objects.get(id=prompt_id)
                prompt.prompt = prompt_text  # Assign correct value
                prompt.system_role = role
                prompt.save(current_user=request.user)
                return JsonResponse({"id": prompt.id}, status=200)
            except Prompt.DoesNotExist:
                return JsonResponse({"error": "Prompt not found"}, status=404)
        else:
            # Create a new prompt
            new_prompt = Prompt(
                project=project,
                prompt=prompt_text,
                system_role=role)
            new_prompt.save(current_user=request.user)
            return JsonResponse({"id": new_prompt.id}, status=200)

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def load_prompt(request):
    """Generates a default markdown description for a project."""
    if request.method == "POST":
        data = json.loads(request.body)
        prompt_id = data.get("prompt_id")
        try:
            prompt = Prompt.objects.get(id=prompt_id)
            return JsonResponse({"id": prompt.id,
                                 "prompt": prompt.prompt,
                                 "role": prompt.system_role}, status=200)
        except Prompt.DoesNotExist:
            return JsonResponse({"error": "Prompt not found"}, status=404)
    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def get_prompts(request):
    """Returns all prompts for a project."""
    if request.method == "POST":
        project = TWFView.s_get_project(request)
        prompts = Prompt.objects.filter(project=project)
        prompt_list = []
        for prompt in prompts:
            prompt_list.append({
                "id": prompt.id,
                "prompt": prompt.prompt,
                "role": prompt.system_role
            })
        return JsonResponse({"prompts": prompt_list}, status=200, safe=False)
    return JsonResponse({"error": "Invalid request"}, status=400)
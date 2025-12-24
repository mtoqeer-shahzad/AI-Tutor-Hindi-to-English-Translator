from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import subprocess
import json

@csrf_exempt
def translate_text(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=400)

    try:
        body = json.loads(request.body.decode("utf-8"))
        text = body.get("text", "")

        if not text:
            return JsonResponse({"error": "Text is required"}, status=400)

        # Improved prompt for Romanized Hindi/Urdu to English translation
        prompt = f"""Translate the following Romanized Hindi/Urdu text to proper English. The text is Hindi/Urdu written in English letters (Roman script). Provide ONLY the English translation without any explanations.

Romanized Hindi/Urdu: {text}

English translation:"""

        ollama_cmd = [
            r"C:\Users\M C\AppData\Local\Programs\Ollama\ollama.exe",
            "run", "llama3.2:latest",
            prompt
        ]

        result = subprocess.run(
            ollama_cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=30  # Added timeout to prevent hanging
        )

        output = result.stdout.strip()

        if not output:
            return JsonResponse({"error": "Empty response from Ollama"}, status=500)

        # Clean up the response (remove any extra text)
        translation = output.split('\n')[0].strip()
        
        # Remove common prefixes that the model might add
        prefixes_to_remove = [
            "English translation:",
            "Translation:",
            "The translation is:",
            "Here is the translation:",
        ]
        
        for prefix in prefixes_to_remove:
            if translation.lower().startswith(prefix.lower()):
                translation = translation[len(prefix):].strip()
                break

        return JsonResponse({"translated_text": translation})

    except subprocess.TimeoutExpired:
        return JsonResponse({"error": "Translation timeout"}, status=504)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
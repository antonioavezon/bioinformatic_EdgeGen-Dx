from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import os
import sys

# Importar lógica del proyecto
# Ajuste de path para que encuentre src desde web_interface/..
sys.path.append(str(settings.BASE_DIR.parent))

try:
    from src.ingestion import create_dummy_fastq
    from src.inference import EdgeInference
except ImportError as e:
    print(f"Error importando core: {e}")
    create_dummy_fastq = None
    EdgeInference = None

# Instancia global
try:
    if EdgeInference:
        engine = EdgeInference(model_path=os.path.join(settings.BASE_DIR.parent, 'data', 'models', 'edgegen_quant.tflite'))
        MODEL_STATUS = "ONLINE"
    else:
        engine = None
        MODEL_STATUS = "OFFLINE"
except Exception as e:
    engine = None
    MODEL_STATUS = f"OFFLINE ({e})"

def index(request):
    return render(request, 'dashboard/index.html', {'status': MODEL_STATUS})

def run_analysis(request):
    if engine is None:
        return JsonResponse({'error': 'Motor de IA no disponible'}, status=503)
    
    try:
        sample_path = create_dummy_fastq()
        results = []
        virus_count = 0
        total_analyzed = 10
        
        with open(sample_path, 'r') as f:
            lines = f.readlines()
            
        for i in range(total_analyzed):
            if (i*4 + 1) >= len(lines): break
            header = lines[i*4].strip()
            sequence = lines[i*4 + 1].strip()
            
            pathogen, confidence, latency = engine.predict(sequence)
            is_viral = "Viral" in pathogen
            if is_viral: virus_count += 1
            
            results.append({
                'id': header,
                'prediction': pathogen,
                'confidence': f"{confidence*100:.1f}%",
                'latency': f"{latency:.2f}ms",
                'is_viral': is_viral
            })
            
        diagnosis = "DETECTADO - SARS-CoV-2" if virus_count > 0 else "NEGATIVO"
        
        return JsonResponse({
            'results': results,
            'diagnosis': diagnosis,
            'virus_count': virus_count
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

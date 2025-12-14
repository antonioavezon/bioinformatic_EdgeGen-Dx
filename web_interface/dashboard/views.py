from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.conf import settings
import os
import sys

# Ajuste de path para que encuentre src
sys.path.append(str(settings.BASE_DIR.parent))

try:
    from src.ingestion import create_dummy_fastq
    from src.inference import EdgeInference
except ImportError as e:
    print(f"Error importando core: {e}")
    create_dummy_fastq = None
    EdgeInference = None

# Instancia global de motores
engines = {}

def get_engine(virus_type='covid19'):
    global engines
    # Map virus type to filename
    # Assuming standard names from train.py
    model_map = {
        'covid19': 'model_covid.tflite',
        'h3n2': 'model_h3n2.tflite'
    }
    
    # Check if loaded
    if virus_type in engines and engines[virus_type] is not None:
        return engines[virus_type]
        
    # Load if not
    filename = model_map.get(virus_type)
    if not filename: return None
    
    try:
        model_path = os.path.join(settings.BASE_DIR.parent, 'data', 'models', filename)
        if os.path.exists(model_path):
            engines[virus_type] = EdgeInference(model_path=model_path)
    except Exception as e:
        print(f"Error loading {virus_type}: {e}")
        engines[virus_type] = None
        
    return engines.get(virus_type)

@ensure_csrf_cookie
def index(request):
    """Renderiza el dashboard."""
    # Check general status (at least one model available?)
    eng_covid = get_engine('covid19')
    eng_h3n2 = get_engine('h3n2')
    
    status = "ONLINE" if (eng_covid or eng_h3n2) else "OFFLINE (No models)"
    return render(request, 'dashboard/index.html', {'status': status})

def run_analysis(request):
    """Maneja el análisis (POST)"""
    # Get selected virus (default covid)
    target_virus = request.POST.get('virus_type', 'covid19')
    
    eng = get_engine(target_virus)
    if eng is None:
        return JsonResponse({'error': f"Model for {target_virus} not ready or training in progress."}, status=503)
    
    try:
        results = []
        virus_count = 0
        
        # --- MODO 1: Archivo Subido ---
        lines = []
        if request.FILES.get('file'):
            uploaded_file = request.FILES['file']
            for chunk in uploaded_file.chunks():
                chunk_str = chunk.decode('utf-8', errors='ignore')
                lines.extend(chunk_str.split('\n'))
                if len(lines) > 200: break # Limit
        
        # --- MODO 2: Texto Manual ---
        elif request.POST.get('sequence'):
            raw_seq = request.POST.get('sequence')
            lines = ["@Manual_Input", raw_seq, "+", "III"]
            
        # --- MODO 3: Simulación (Fallback) ---
        else:
            # We don't have separate dummy files yet, reuse standard or generate on fly?
            # Re-using covid dummy is fine for demo structure, but let's just use existing func
            sample_path = create_dummy_fastq()
            with open(sample_path, 'r') as f:
                lines = f.readlines()
                
        # Analyze
        is_fastq = any((l.startswith('@') for l in lines[:5]))
        
        for i in range(min(20, len(lines))):
            header = "Seq"
            seq = ""
            
            if is_fastq and i*4+1 < len(lines):
                header = lines[i*4].strip()
                seq = lines[i*4+1].strip()
            elif not is_fastq:
                # Line by line raw
                seq = lines[i].strip()
                header = f"Read_{i}"
            
            if len(seq) < 10: continue
            
            # Determine display name
            viral_label = "SARS-CoV-2" if target_virus == 'covid19' else "Influenza H3N2"
            _analyze_read(eng, header, seq, results_list, viral_label)
            if results[-1]['is_viral']: virus_count += 1
        
        # Diagnosis
        virus_name = "SARS-CoV-2" if target_virus == 'covid19' else "Influenza H3N2"
        diagnosis = f"DETECTADO - {virus_name}" if virus_count > 0 else "NEGATIVO"
        
        return JsonResponse({
            'results': results,
            'diagnosis': diagnosis,
            'virus_count': virus_count
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

def _analyze_read(engine, header, sequence, results_list, viral_name_label):
    pathogen_tag, confidence, latency = engine.predict(sequence)
    is_viral = "Viral" in pathogen_tag
    
    final_prediction = f"⚠️ {viral_name_label} (Viral)" if is_viral else "✓ Negativo (Clean)"

    results_list.append({
        'id': header,
        'prediction': final_prediction,
        'confidence': f"{confidence*100:.1f}%",
        'latency': f"{latency:.2f}ms",
        'is_viral': is_viral
    })

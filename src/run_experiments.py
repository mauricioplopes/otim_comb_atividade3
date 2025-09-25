#!/usr/bin/env python3
"""
run_experiments_robust.py

Captura de timeout em tempo real.
Usa threading para monitorar a saída em tempo real e capturar progresso.
"""

import os
import sys
import time
import csv
import subprocess
import threading
import queue
from datetime import datetime
from pathlib import Path


class RobustExperimentRunner:
    """Runner com captura em tempo real de resultados parciais."""
    
    def __init__(self, instances_dir="instances/qbf_sc", results_file="experiment_results.csv", 
                 timeout_minutes=30, max_iterations=100000):
        self.instances_dir = Path(instances_dir)
        self.results_file = results_file
        self.timeout_seconds = timeout_minutes * 60
        self.max_iterations = max_iterations
        
        # Configurações dos experimentos
        self.configurations = [
            {
                'name': 'PADRAO',
                'description': 'First-improving + T1=20 + Estratégia Padrão',
                'method': 'first-improving',
                'tenure': 20,
                'extra_params': []
            },
            {
                'name': 'PADRAO_BEST',
                'description': 'Best-improving + T1=20 + Estratégia Padrão',
                'method': 'best-improving',
                'tenure': 20,
                'extra_params': []
            },
            {
                'name': 'PADRAO_TENURE',
                'description': 'First-improving + T2=50 + Estratégia Padrão',
                'method': 'first-improving',
                'tenure': 50,
                'extra_params': []
            },
            {
                'name': 'PADRAO_METHOD1',
                'description': 'First-improving + T1=20 + Probabilistic TS',
                'method': 'probabilistic',
                'tenure': 20,
                'extra_params': ['alpha=2.0']
            },
            {
                'name': 'PADRAO_METHOD2',
                'description': 'First-improving + T1=20 + Intensification by Neighborhood',
                'method': 'intensification',
                'tenure': 20,
                'extra_params': ['elite=5', 'period=50']
            }
        ]
        
        self._validate_setup()
    
    def _validate_setup(self):
        """Validações básicas."""
        if not self.instances_dir.exists():
            raise FileNotFoundError(f"Diretório de instâncias não encontrado: {self.instances_dir}")
        
        if not Path("main.py").exists():
            raise FileNotFoundError("main.py não encontrado no diretório atual")
        
        instances = list(self.instances_dir.glob("instance-*.txt"))
        print(f"✓ Encontradas {len(instances)} instâncias")
        print(f"✓ Configurado para {len(self.configurations)} configurações")
        print(f"✓ Limite de tempo: {self.timeout_seconds/60:.2f} minutos por experimento")
    
    def get_instances(self):
        """Retorna lista das instâncias ordenadas."""
        instances = []
        for i in range(1, 16):
            instance_file = self.instances_dir / f"instance-{i:02d}.txt"
            if instance_file.exists():
                instances.append(instance_file)
        return instances
    
    def stream_reader(self, stream, stream_name, output_queue, stop_event):
        """Thread para ler stream em tempo real."""
        try:
            while not stop_event.is_set():
                line = stream.readline()
                if line:
                    output_queue.put((stream_name, line.strip()))
                else:
                    break
        except Exception as e:
            output_queue.put(('error', f"Erro lendo {stream_name}: {str(e)}"))
        finally:
            try:
                stream.close()
            except:
                pass
    
    def run_single_experiment(self, config, instance_path):
        """Executa experimento com monitoramento em tempo real."""
        
        cmd = [
            "python", "main.py",
            str(config['tenure']),
            str(self.max_iterations),
            str(instance_path),
            f"method={config['method']}",
            "seed=42"
        ]
        cmd.extend(config['extra_params'])
        
        print(f"  Executando: {' '.join(cmd)}")
        
        # Estado do progresso
        progress = {
            'best_value': 0.0,
            'best_solution': '[]',
            'iterations': 0,
            'improvements': 0,
            'all_lines': []
        }
        
        start_time = time.time()
        
        try:
            # Inicia processo
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Queue para comunicação entre threads
            output_queue = queue.Queue()
            stop_event = threading.Event()
            
            # Threads para ler stdout e stderr
            stdout_thread = threading.Thread(
                target=self.stream_reader,
                args=(process.stdout, 'stdout', output_queue, stop_event),
                daemon=True
            )
            stderr_thread = threading.Thread(
                target=self.stream_reader,
                args=(process.stderr, 'stderr', output_queue, stop_event),
                daemon=True
            )
            
            stdout_thread.start()
            stderr_thread.start()
            
            # Monitora processo
            while True:
                current_time = time.time()
                elapsed = current_time - start_time
                
                # Verifica se processo terminou
                return_code = process.poll()
                if return_code is not None:
                    stop_event.set()
                    
                    # Captura saída restante
                    remaining_timeout = time.time() + 1
                    while time.time() < remaining_timeout:
                        try:
                            stream_name, line = output_queue.get_nowait()
                            self._update_progress(line, progress)
                        except queue.Empty:
                            break
                    
                    if return_code == 0:
                        return self._create_result('SUCCESS', config, instance_path, 
                                                 elapsed, progress)
                    else:
                        return self._create_result('ERROR', config, instance_path, 
                                                 elapsed, progress, "Erro na execução")
                
                # Verifica timeout
                if elapsed > self.timeout_seconds:
                    print(f"    ⏰ Timeout após {elapsed:.1f}s")
                    
                    # Para processo
                    try:
                        process.terminate()
                        process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                    
                    stop_event.set()
                    
                    return self._create_result('TIMEOUT', config, instance_path, 
                                             elapsed, progress, 
                                             f"Timeout após {self.timeout_seconds/60:.1f} minutos")
                
                # Processa saída disponível
                try:
                    stream_name, line = output_queue.get(timeout=0.5)
                    self._update_progress(line, progress)
                    
                    # Mostra progresso importante
                    if "Nova melhor" in line and progress['best_value'] > 0:
                        print(f"    📈 Progresso: {progress['best_value']:.3f} "
                              f"(iter ~{progress['iterations']})")
                
                except queue.Empty:
                    continue
                except Exception as e:
                    continue
        
        except Exception as e:
            elapsed = time.time() - start_time
            return self._create_result('EXCEPTION', config, instance_path, 
                                     elapsed, progress, str(e))
    
    def _update_progress(self, line, progress):
        """Atualiza progresso baseado em linha de saída."""
        if not line:
            return
        
        progress['all_lines'].append(line)
        line_lower = line.lower()
        
        try:
            # Procura melhorias
            if "nova melhor" in line_lower or "new best" in line_lower:
                progress['improvements'] += 1
                
                # Extrai custo
                if "cost=[" in line:
                    cost_start = line.find("cost=[") + 6
                    cost_end = line.find("]", cost_start)
                    if cost_end > cost_start:
                        cost = float(line[cost_start:cost_end])
                        value = -cost  # QBF inversa
                        if value > progress['best_value']:
                            progress['best_value'] = value
                
                # Extrai iteração
                if "(iter." in line_lower:
                    iter_start = line.lower().find("(iter.") + 6
                    iter_end = line.find(")", iter_start)
                    if iter_end > iter_start:
                        try:
                            iteration = int(line[iter_start:iter_end])
                            if iteration > progress['iterations']:
                                progress['iterations'] = iteration
                        except ValueError:
                            pass
                
                # Extrai elementos
                if "elements=[" in line:
                    elem_start = line.find("elements=[")
                    elem_end = line.find("]", elem_start) + 1
                    if elem_end > elem_start:
                        elements = line[elem_start + 9:elem_end]
                        if elements and elements != "":
                            progress['best_solution'] = elements
            
            # Procura resultado final
            elif "valor real qbf:" in line_lower:
                try:
                    value_part = line.split(":")[-1].strip()
                    value = float(value_part)
                    if value > progress['best_value']:
                        progress['best_value'] = value
                except (ValueError, IndexError):
                    pass
            
            elif "elementos:" in line_lower and "[" in line:
                try:
                    solution_part = line.split(":", 1)[1].strip()
                    if solution_part and solution_part != "[]":
                        progress['best_solution'] = solution_part
                except IndexError:
                    pass
            
            # Fallback: solução inicial
            elif ("solu" in line_lower and "inicial" in line_lower and 
                  progress['best_value'] == 0.0):
                if "cost=[" in line:
                    cost_start = line.find("cost=[") + 6
                    cost_end = line.find("]", cost_start)
                    if cost_end > cost_start:
                        cost = float(line[cost_start:cost_end])
                        progress['best_value'] = -cost
                
                if "elements=[" in line and progress['best_solution'] == "[]":
                    elem_start = line.find("elements=[")
                    elem_end = line.find("]", elem_start) + 1
                    if elem_end > elem_start:
                        progress['best_solution'] = line[elem_start + 9:elem_end]
        
        except (ValueError, IndexError):
            # Ignora erros de parsing - continua processamento
            pass
    
    def _create_result(self, status, config, instance_path, elapsed, progress, error_msg=""):
        """Cria resultado padronizado."""
        
        # Constrói mensagem informativa
        if status == 'TIMEOUT' and progress['best_value'] > 0:
            error_parts = [f"Timeout após {self.timeout_seconds/60:.0f} minutos"]
            error_parts.append(f"Melhor parcial: {progress['best_value']:.3f}")
            if progress['iterations'] > 0:
                error_parts.append(f"Iterações: {progress['iterations']}")
            if progress['improvements'] > 0:
                error_parts.append(f"Melhorias: {progress['improvements']}")
            error_msg = " - ".join(error_parts)
        elif not error_msg and status == 'TIMEOUT':
            error_msg = f"Timeout após {self.timeout_seconds/60:.0f} minutos - Sem resultado parcial"
        
        return {
            'status': status,
            'config_name': config['name'],
            'config_description': config['description'],
            'method': config['method'],
            'tenure': config['tenure'],
            'instance': instance_path.name,
            'instance_path': str(instance_path),
            'objective_value': progress['best_value'],
            'execution_time': elapsed,
            'wall_time': elapsed,
            'solution': progress['best_solution'],
            'iterations_completed': progress['iterations'] if progress['iterations'] > 0 else 'TIMEOUT',
            'termination_reason': status,
            'error_message': error_msg,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def initialize_results_file(self):
        """Inicializa arquivo CSV."""
        fieldnames = [
            'status', 'config_name', 'config_description', 'method', 'tenure',
            'instance', 'instance_path', 'objective_value', 'execution_time', 'wall_time',
            'solution', 'iterations_completed', 'termination_reason', 'error_message', 'timestamp'
        ]
        
        with open(self.results_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
        
        print(f"✓ Arquivo inicializado: {self.results_file}")
    
    def save_result(self, result):
        """Salva resultado no CSV."""
        fieldnames = [
            'status', 'config_name', 'config_description', 'method', 'tenure',
            'instance', 'instance_path', 'objective_value', 'execution_time', 'wall_time',
            'solution', 'iterations_completed', 'termination_reason', 'error_message', 'timestamp'
        ]
        
        with open(self.results_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
            writer.writerow(result)
    
    def run_all_experiments(self):
        """Executa todos os experimentos."""
        instances = self.get_instances()
        total = len(self.configurations) * len(instances)
        
        print(f"\n{'='*60}")
        print(f"EXPERIMENTOS - ATIVIDADE 3")
        print(f"{'='*60}")
        print(f"⚡ Captura em tempo real de progresso")
        print(f"🔧 Total: {total} experimentos")
        print(f"⏰ {self.timeout_seconds/60:.1f} min por experimento")
        print(f"{'='*60}\n")
        
        self.initialize_results_file()
        
        count = 0
        start_global = time.time()
        
        for config in self.configurations:
            print(f"\n[CONFIG] {config['name']}")
            print("-" * 40)
            
            for instance in instances:
                count += 1
                print(f"[{count:2d}/{total}] {instance.name}")
                
                result = self.run_single_experiment(config, instance)
                self.save_result(result)
                
                # Relatório
                if result['status'] == 'SUCCESS':
                    print(f"  ✅ Sucesso: {result['objective_value']:.3f}")
                elif result['status'] == 'TIMEOUT':
                    if result['objective_value'] > 0:
                        print(f"  ⏰ Timeout: Parcial={result['objective_value']:.3f} "
                              f"(iter {result['iterations_completed']})")
                    else:
                        print(f"  ⏰ Timeout: Sem resultado parcial")
                else:
                    print(f"  ❌ {result['status']}")
        
        total_time = time.time() - start_global
        print(f"\n{'='*60}")
        print(f"✅ CONCLUÍDO: {count} experimentos em {total_time/60:.1f} min")
        print(f"📁 Resultados: {self.results_file}")
        print(f"{'='*60}")


def main():
    """Função principal."""
    runner = RobustExperimentRunner(
        instances_dir="instances/qbf_sc",
        results_file="experiment_results.csv",
        timeout_minutes=30,
        max_iterations=10000
    )
    
    try:
        runner.run_all_experiments()
        return 0
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
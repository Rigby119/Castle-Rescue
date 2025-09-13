# -*- coding: utf-8 -*-
"""
Simulador Castle Rescue - 1000 simulaciones del sistema estratégico
Analiza cuántas simulaciones logran salvar más de 5 víctimas
"""

import sys
import os
import time
from collections import Counter

# Importar el módulo strategicSystem
# Asumiendo que el archivo se llama strategicSystem.py y está en el mismo directorio
try:
    from strategicSystem import CastleRescueModel, SoldierAgent
    print("✓ Módulo strategicSystem importado correctamente")
except ImportError as e:
    print(f"Error al importar strategicSystem: {e}")
    print("Asegúrate de que el archivo strategicSystem.py esté en el mismo directorio")
    sys.exit(1)

def run_single_simulation(sim_num, max_steps=500, verbose=False):
    """
    Ejecuta una simulación individual del Castle Rescue
    
    Args:
        sim_num (int): Número de la simulación
        max_steps (int): Máximo número de pasos antes de detener
        verbose (bool): Si mostrar información detallada
    
    Returns:
        dict: Resultado de la simulación
    """
    try:
        # Crear el modelo
        model = CastleRescueModel(width=10, height=8, agents=6)
        
        step_count = 0
        
        # Ejecutar hasta que termine el juego o se alcance el límite de pasos
        while not model.finish_game() and step_count < max_steps:
            model.step()
            step_count += 1
            
            if verbose and step_count % 50 == 0:
                print(f"  Simulación {sim_num}: Paso {step_count}, Víctimas salvadas: {model.victims_saved}")
        
        # Recopilar resultados
        result = {
            'simulation': sim_num,
            'victims_saved': model.victims_saved,
            'victims_dead': model.victims_dead,
            'damage_counter': model.damage_counter,
            'steps': step_count,
            'finished': model.finished if hasattr(model, 'finished') else (step_count < max_steps),
            'win': model.win if hasattr(model, 'win') else (model.victims_saved >= 7),
            'reason': model.reason if hasattr(model, 'reason') else 'unknown'
        }
        
        if verbose:
            status = "GANÓ" if result['win'] else "PERDIÓ"
            print(f"  Simulación {sim_num} terminó: {status} - Víctimas salvadas: {result['victims_saved']}")
        
        return result
        
    except Exception as e:
        print(f"Error en simulación {sim_num}: {e}")
        return {
            'simulation': sim_num,
            'victims_saved': 0,
            'victims_dead': 0,
            'damage_counter': 0,
            'steps': 0,
            'finished': False,
            'win': False,
            'reason': 'error',
            'error': str(e)
        }

def run_batch_simulations(num_simulations=1000, max_steps=500):
    """
    Ejecuta múltiples simulaciones y analiza los resultados
    
    Args:
        num_simulations (int): Número de simulaciones a ejecutar
        max_steps (int): Máximo número de pasos por simulación
    
    Returns:
        dict: Análisis completo de los resultados
    """
    print(f"🎮 Iniciando {num_simulations} simulaciones del Castle Rescue System")
    print("=" * 60)
    
    results = []
    start_time = time.time()
    
    # Ejecutar simulaciones
    for i in range(1, num_simulations + 1):
        if i % 100 == 0:
            elapsed = time.time() - start_time
            print(f"Progreso: {i}/{num_simulations} simulaciones completadas ({elapsed:.1f}s)")
        
        result = run_single_simulation(i, max_steps, verbose=(i <= 5))  # Verbose solo para las primeras 5
        results.append(result)
    
    # Análisis de resultados
    print(f"\n📊 ANÁLISIS DE RESULTADOS ({num_simulations} simulaciones)")
    print("=" * 60)
    
    # Simulaciones que salvaron más de 5 víctimas
    more_than_5 = [r for r in results if r['victims_saved'] > 5]
    
    print(f"🏆 Simulaciones que salvaron MÁS DE 5 víctimas: {len(more_than_5)}")
    print(f"📈 Porcentaje de éxito (>5 víctimas): {len(more_than_5)/num_simulations*100:.1f}%")
    
    if more_than_5:
        print(f"\n📋 DETALLES DE SIMULACIONES EXITOSAS (>5 víctimas):")
        print("-" * 50)
        for result in more_than_5:
            print(f"Simulación {result['simulation']:3d}: {result['victims_saved']} víctimas salvadas "
                  f"(Pasos: {result['steps']}, Muertes: {result['victims_dead']}, "
                  f"Daño: {result['damage_counter']})")
    
    # Estadísticas generales
    victims_saved_counts = Counter(r['victims_saved'] for r in results)
    total_steps = sum(r['steps'] for r in results)
    total_wins = sum(1 for r in results if r['win'])
    
    print(f"\n📈 ESTADÍSTICAS GENERALES:")
    print("-" * 30)
    print(f"Total de victorias (≥7 víctimas): {total_wins}")
    print(f"Porcentaje de victorias: {total_wins/num_simulations*100:.1f}%")
    print(f"Promedio de víctimas salvadas: {sum(r['victims_saved'] for r in results)/num_simulations:.2f}")
    print(f"Promedio de pasos por simulación: {total_steps/num_simulations:.1f}")
    print(f"Tiempo total de ejecución: {time.time() - start_time:.1f} segundos")
    
    print(f"\n📊 DISTRIBUCIÓN DE VÍCTIMAS SALVADAS:")
    print("-" * 40)
    for victims in sorted(victims_saved_counts.keys()):
        count = victims_saved_counts[victims]
        percentage = count/num_simulations*100
        bar = "█" * int(percentage/2)  # Barra visual
        print(f"{victims:2d} víctimas: {count:4d} veces ({percentage:5.1f}%) {bar}")
    
    # Razones de finalización
    reasons = Counter(r['reason'] for r in results if 'reason' in r)
    if reasons:
        print(f"\n🔍 RAZONES DE FINALIZACIÓN:")
        print("-" * 30)
        for reason, count in reasons.most_common():
            print(f"{reason}: {count} veces ({count/num_simulations*100:.1f}%)")
    
    return {
        'results': results,
        'more_than_5': more_than_5,
        'victims_saved_distribution': victims_saved_counts,
        'total_wins': total_wins,
        'success_rate_more_than_5': len(more_than_5)/num_simulations,
        'win_rate': total_wins/num_simulations,
        'average_victims_saved': sum(r['victims_saved'] for r in results)/num_simulations,
        'average_steps': total_steps/num_simulations,
        'execution_time': time.time() - start_time
    }

if __name__ == "__main__":
    # Configuración
    NUM_SIMULATIONS = 1000
    MAX_STEPS_PER_SIM = 500  # Límite de pasos para evitar simulaciones infinitas
    
    print("🏰 CASTLE RESCUE - SIMULADOR ESTRATÉGICO")
    print("Analizando el rendimiento del sistema estratégico")
    print(f"Configuración: {NUM_SIMULATIONS} simulaciones, máx {MAX_STEPS_PER_SIM} pasos/sim")
    print()
    
    # Ejecutar simulaciones
    analysis = run_batch_simulations(NUM_SIMULATIONS, MAX_STEPS_PER_SIM)
    
    # Resumen final
    print(f"\n🎯 RESUMEN EJECUTIVO:")
    print("=" * 50)
    print(f"• Simulaciones exitosas (>5 víctimas): {len(analysis['more_than_5'])}/{NUM_SIMULATIONS}")
    print(f"• Tasa de éxito (>5 víctimas): {analysis['success_rate_more_than_5']*100:.1f}%")
    print(f"• Victorias completas (≥7 víctimas): {analysis['total_wins']}")
    print(f"• Tasa de victoria: {analysis['win_rate']*100:.1f}%")
    print(f"• Promedio de víctimas salvadas: {analysis['average_victims_saved']:.2f}")
    
    if analysis['more_than_5']:
        victims_in_successful = [r['victims_saved'] for r in analysis['more_than_5']]
        print(f"• En simulaciones exitosas (>5), promedio: {sum(victims_in_successful)/len(victims_in_successful):.2f} víctimas")
    
    print(f"\n✅ Análisis completado en {analysis['execution_time']:.1f} segundos")
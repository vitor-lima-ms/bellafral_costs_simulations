from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib import messages
from bellafral.my_forms import BellafralForm, BellafralSimulatorForm
from bellafral.models import Bellafral, Simulations
from base_dir.functions import get_total_cost
import csv

# Create your views here.

def bellafral_form(request):
    if request.method == 'POST':
        form = BellafralForm(request.POST)
        if form.is_valid():
            for value in form.cleaned_data.values():
                if type(value) == str or value == None:
                    continue
                elif value < 0:
                    messages.error(request, 'Valores não podem ser negativos')
                    return redirect('bellafral:bellafral_form')

            form.save()
            messages.success(request, 'Fralda criada com sucesso')
            return redirect('bellafral:bellafral_list')
    else:
        form = BellafralForm()
    return render(request, 'bellafral_form.html', {'form': form})

def bellafral_list(request):
    bellafral = Bellafral.objects.all()
    return render(request, 'bellafral_list.html', {'bellafral': bellafral})

def bellafral_details(request, id):
    fralda = get_object_or_404(Bellafral, id=id)
    return render(request, 'bellafral_details.html', {'fralda': fralda})

def bellafral_delete(request, id):
    fralda = get_object_or_404(Bellafral, id=id)
    fralda.delete()
    return redirect('bellafral:bellafral_list')

def bellafral_pre_simulator(request):
    form = BellafralSimulatorForm()
    return render(request, 'bellafral_pre_simulator.html', {'form': form})

def bellafral_simulator(request):
    if request.method == 'POST':
            form = BellafralSimulatorForm(request.POST)
                        
            if form.is_valid():
                fralda = form.cleaned_data['fralda']
                costs = form.cleaned_data['costs']
    else:
        form = BellafralSimulatorForm()
        return render(request, 'bellafral_pre_simulator.html', {'form': form})

    total_cost = get_total_cost(fralda, costs)

    simulation = Simulations.objects.create(
        fralda_object=fralda,
        costs_object=costs,
        )
    simulation.save()

    fralda.celulose_virgem_total_unit_cost = round(fralda.celulose_virgem * costs.celulose_virgem_price, 4)
    fralda.gel_total_unit_cost = round(fralda.gel * costs.gel_price, 4)
    fralda.tnt_filtrante_780_total_unit_cost = round(fralda.tnt_filtrante_780 * costs.tnt_filtrante_780_price, 4)
    fralda.fita_adesiva_tape_total_unit_cost = round(fralda.fita_adesiva_tape * costs.fita_adesiva_tape_price, 4)
    fralda.elastico_elastano_lycra_total_unit_cost = round(fralda.elastico_elastano_lycra * costs.elastico_elastano_lycra_price, 4)
    fralda.barreira_total_unit_cost = round(fralda.barreira * costs.barreira_price, 4)
    fralda.polietileno_filme_780_total_unit_cost = round(fralda.polietileno_filme_780 * costs.polietileno_filme_780_price, 4)
    fralda.hot_melt_const_total_unit_cost = round(fralda.hot_melt_const * costs.hot_melt_const_price, 4)

    fralda.save()
    
    return render(request, 'bellafral_simulator.html', {'total_cost': total_cost, 'simulation': simulation})

def download_simulation(request, id):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="simulation.csv"'

    csv_writer = csv.writer(response)

    simulation = get_object_or_404(Simulations, id=id)
    total_cost = get_total_cost(simulation.fralda_object, simulation.costs_object)

    csv_writer.writerow(
        [
            'Item',
            'Quantidade',
            'Custo unitário',
            'Custo total',
        ]
    )

    csv_writer.writerow(
        [
            'Celulose virgem (Kg)',
            simulation.fralda_object.celulose_virgem,
            simulation.costs_object.celulose_virgem_price,
            round(simulation.fralda_object.celulose_virgem * simulation.costs_object.celulose_virgem_price, 4),
        ]
    )

    csv_writer.writerow(
        [
            'Gel (Kg)',
            simulation.fralda_object.gel,
            simulation.costs_object.gel_price,
            round(simulation.fralda_object.gel * simulation.costs_object.gel_price, 4),
        ]
    )

    csv_writer.writerow(
        [
            'TNT - Filtrante - 780mm (m2)',
            simulation.fralda_object.tnt_filtrante_780,
            simulation.costs_object.tnt_filtrante_780_price,
            round(simulation.fralda_object.tnt_filtrante_780 * simulation.costs_object.tnt_filtrante_780_price, 4),
        ]
    )

    csv_writer.writerow(
        [
            'Fita adesiva - Tape (Kg)',
            simulation.fralda_object.fita_adesiva_tape,
            simulation.costs_object.fita_adesiva_tape_price,
            round(simulation.fralda_object.fita_adesiva_tape * simulation.costs_object.fita_adesiva_tape_price, 4),
        ]
    )

    csv_writer.writerow(
        [
            'Elástico - Elastano - Lycra (Kg)',
            simulation.fralda_object.elastico_elastano_lycra,
            simulation.costs_object.elastico_elastano_lycra_price,
            round(simulation.fralda_object.elastico_elastano_lycra * simulation.costs_object.elastico_elastano_lycra_price, 4),
        ]
    )

    csv_writer.writerow(
        [
            'Barreira (m2)',
            simulation.fralda_object.barreira,
            simulation.costs_object.barreira_price,
            round(simulation.fralda_object.barreira * simulation.costs_object.barreira_price, 4),
        ]
    )

    csv_writer.writerow(
        [
            'Polietileno - Filme - 780mm (Kg)',
            simulation.fralda_object.polietileno_filme_780,
            simulation.costs_object.polietileno_filme_780_price,
            round(simulation.fralda_object.polietileno_filme_780 * simulation.costs_object.polietileno_filme_780_price, 4),
        ]
    )

    csv_writer.writerow(
        [
            'Hot-Melt Construção (Kg)',
            simulation.fralda_object.hot_melt_const,
            simulation.costs_object.hot_melt_const_price,
            round(simulation.fralda_object.hot_melt_const * simulation.costs_object.hot_melt_const_price, 4),
        ]
    )

    csv_writer.writerow(
        [
            'Custo total',
            total_cost,
        ]
    )
    
    return response

def simulator_list(request):
    simulations = Simulations.objects.all()
    return render(request, 'simulator_list.html', {'simulations': simulations})

def simulator_details(request, id):
    simulation = get_object_or_404(Simulations, id=id)
    total_cost = get_total_cost(simulation.fralda_object, simulation.costs_object)

    total_unit_cost = {
        'celulose_virgem': round(simulation.costs_object.celulose_virgem_price * simulation.fralda_object.celulose_virgem, 4),
        'gel': round(simulation.costs_object.gel_price * simulation.fralda_object.gel, 4),
        'tnt_filtrante_780': round(simulation.costs_object.tnt_filtrante_780_price * simulation.fralda_object.tnt_filtrante_780, 4),
        'fita_adesiva_tape': round(simulation.costs_object.fita_adesiva_tape_price * simulation.fralda_object.fita_adesiva_tape, 4),
        'elastico_elastano_lycra': round(simulation.costs_object.elastico_elastano_lycra_price * simulation.fralda_object.elastico_elastano_lycra, 4),
        'barreira': round(simulation.costs_object.barreira_price * simulation.fralda_object.barreira, 4),
        'polietileno_filme_780': round(simulation.costs_object.polietileno_filme_780_price * simulation.fralda_object.polietileno_filme_780, 4),
        'hot_melt_const': round(simulation.costs_object.hot_melt_const_price * simulation.fralda_object.hot_melt_const, 4),
    }

    return render(request, 'simulator_details.html', {'simulation': simulation, 'total_cost': total_cost, 'total_unit_cost': total_unit_cost})

def simulator_delete(request, id):
    simulation = get_object_or_404(Simulations, id=id)
    simulation.delete()
    return redirect('bellafral:simulator_list')

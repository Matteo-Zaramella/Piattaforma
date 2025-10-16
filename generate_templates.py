"""
Script per generare i template HTML mancanti
"""
import os

TEMPLATES_DIR = "templates"

# Template per Edit Matched Betting
edit_mb_template = """{% extends "base.html" %}

{% block title %}Modifica Scommessa - Piattaforma{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-8 offset-md-2">
        <div class="card">
            <div class="card-header bg-warning text-white">
                <h4 class="mb-0"><i class="bi bi-pencil"></i> Modifica Scommessa</h4>
            </div>
            <div class="card-body">
                <form method="POST">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Bookmaker Back *</label>
                            <input type="text" name="bookmaker_back" class="form-control" value="{{ bet.bookmaker_back }}" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Bookmaker Lay</label>
                            <input type="text" name="bookmaker_lay" class="form-control" value="{{ bet.bookmaker_lay if bet.bookmaker_lay }}">
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-3 mb-3">
                            <label class="form-label">Stake Back *</label>
                            <input type="number" step="0.01" name="stake_back" class="form-control" value="{{ bet.stake_back }}" required>
                        </div>
                        <div class="col-md-3 mb-3">
                            <label class="form-label">Quota Back *</label>
                            <input type="number" step="0.01" name="quota_back" class="form-control" value="{{ bet.quota_back }}" required>
                        </div>
                        <div class="col-md-3 mb-3">
                            <label class="form-label">Stake Lay</label>
                            <input type="number" step="0.01" name="stake_lay" class="form-control" value="{{ bet.stake_lay if bet.stake_lay }}">
                        </div>
                        <div class="col-md-3 mb-3">
                            <label class="form-label">Quota Lay</label>
                            <input type="number" step="0.01" name="quota_lay" class="form-control" value="{{ bet.quota_lay if bet.quota_lay }}">
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Evento *</label>
                            <input type="text" name="evento" class="form-control" value="{{ bet.evento }}" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Data Evento</label>
                            <input type="datetime-local" name="data_evento" class="form-control" value="{{ bet.data_evento if bet.data_evento }}">
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-4 mb-3">
                            <label class="form-label">Rating</label>
                            <select name="rating" class="form-control">
                                <option value="">Seleziona...</option>
                                <option value="SNR" {% if bet.rating == 'SNR' %}selected{% endif %}>SNR</option>
                                <option value="Qualificante" {% if bet.rating == 'Qualificante' %}selected{% endif %}>Qualificante</option>
                                <option value="Reload" {% if bet.rating == 'Reload' %}selected{% endif %}>Reload</option>
                                <option value="Altro" {% if bet.rating == 'Altro' %}selected{% endif %}>Altro</option>
                            </select>
                        </div>
                        <div class="col-md-4 mb-3">
                            <label class="form-label">Mercato</label>
                            <input type="text" name="mercato" class="form-control" value="{{ bet.mercato if bet.mercato }}">
                        </div>
                        <div class="col-md-4 mb-3">
                            <label class="form-label">Profitto</label>
                            <input type="number" step="0.01" name="profitto" class="form-control" value="{{ bet.profitto }}">
                        </div>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Offerta</label>
                        <input type="text" name="offerta" class="form-control" value="{{ bet.offerta if bet.offerta }}">
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Note</label>
                        <textarea name="note" class="form-control" rows="3">{{ bet.note if bet.note }}</textarea>
                    </div>

                    <div class="d-flex justify-content-between">
                        <a href="{{ url_for('matched_betting.index') }}" class="btn btn-secondary">Annulla</a>
                        <button type="submit" class="btn btn-warning">Aggiorna Scommessa</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

# Template per Stats Matched Betting
stats_mb_template = """{% extends "base.html" %}

{% block title %}Statistiche Matched Betting - Piattaforma{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12 mb-4">
        <h1><i class="bi bi-graph-up"></i> Statistiche Matched Betting</h1>
        <a href="{{ url_for('matched_betting.index') }}" class="btn btn-secondary">Torna alla lista</a>
    </div>
</div>

<div class="row mb-4">
    <div class="col-md-4">
        <div class="card">
            <div class="card-body text-center">
                <h6 class="text-muted">Scommesse Totali</h6>
                <h2>{{ stats.total_bets }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card">
            <div class="card-body text-center">
                <h6 class="text-muted">Profitto Totale</h6>
                <h2 class="text-success">&euro; {{ "%.2f"|format(stats.total_profit) }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card">
            <div class="card-body text-center">
                <h6 class="text-muted">Profitto Medio</h6>
                <h2 class="text-info">&euro; {{ "%.2f"|format(stats.avg_profit) }}</h2>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-md-6 mb-4">
        <div class="card">
            <div class="card-header bg-primary text-white">
                Profitto per Bookmaker
            </div>
            <div class="card-body">
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>Bookmaker</th>
                            <th>Scommesse</th>
                            <th>Profitto</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for book in stats.by_bookmaker %}
                        <tr>
                            <td>{{ book.bookmaker_back }}</td>
                            <td>{{ book.count }}</td>
                            <td class="{{ 'text-success' if book.profit >= 0 else 'text-danger' }}">&euro; {{ "%.2f"|format(book.profit) }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <div class="col-md-6 mb-4">
        <div class="card">
            <div class="card-header bg-success text-white">
                Profitto per Mese
            </div>
            <div class="card-body">
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>Mese</th>
                            <th>Scommesse</th>
                            <th>Profitto</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for month in stats.by_month %}
                        <tr>
                            <td>{{ month.month }}</td>
                            <td>{{ month.count }}</td>
                            <td class="{{ 'text-success' if month.profit >= 0 else 'text-danger' }}">&euro; {{ "%.2f"|format(month.profit) }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

# Template base per Task (index)
task_index_template = """{% extends "base.html" %}

{% block title %}{title} - Piattaforma{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12 d-flex justify-content-between align-items-center mb-4">
        <h1><i class="bi {icon}"></i> {title}</h1>
        <a href="{{ url_for('{module}.add') }}" class="btn btn-primary">
            <i class="bi bi-plus-circle"></i> Nuovo Task
        </a>
    </div>
</div>

<div class="row mb-3">
    <div class="col-md-12">
        <div class="btn-group" role="group">
            <a href="?stato=all" class="btn btn-outline-secondary {{ 'active' if filter_stato == 'all' else '' }}">
                Tutti ({{ counts.da_fare + counts.in_corso + counts.completato }})
            </a>
            <a href="?stato=da_fare" class="btn btn-outline-primary {{ 'active' if filter_stato == 'da_fare' else '' }}">
                Da fare ({{ counts.da_fare }})
            </a>
            <a href="?stato=in_corso" class="btn btn-outline-warning {{ 'active' if filter_stato == 'in_corso' else '' }}">
                In corso ({{ counts.in_corso }})
            </a>
            <a href="?stato=completato" class="btn btn-outline-success {{ 'active' if filter_stato == 'completato' else '' }}">
                Completati ({{ counts.completato }})
            </a>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-12">
        {% if tasks %}
            {% for task in tasks %}
            <div class="card mb-3">
                <div class="card-body">
                    <div class="row align-items-center">
                        <div class="col-md-8">
                            <h5>
                                {{ task.titolo }}
                                <span class="badge bg-{{ 'primary' if task.priorita == 'alta' else 'secondary' if task.priorita == 'media' else 'info' }}">
                                    {{ task.priorita }}
                                </span>
                                <span class="badge bg-{{ 'success' if task.stato == 'completato' else 'warning' if task.stato == 'in_corso' else 'secondary' }}">
                                    {{ task.stato }}
                                </span>
                            </h5>
                            <p class="text-muted mb-1">{{ task.descrizione if task.descrizione }}</p>
                            {% if task.deadline %}
                            <small class="text-danger"><i class="bi bi-calendar"></i> Scadenza: {{ task.deadline }}</small>
                            {% endif %}
                        </div>
                        <div class="col-md-4 text-end">
                            <form method="POST" action="{{ url_for('{module}.toggle_status', task_id=task.id) }}" style="display: inline;">
                                <button type="submit" class="btn btn-sm btn-{{ 'success' if task.stato != 'completato' else 'secondary' }}">
                                    <i class="bi bi-check-circle"></i> {{ 'Completa' if task.stato != 'completato' else 'Riapri' }}
                                </button>
                            </form>
                            <a href="{{ url_for('{module}.edit', task_id=task.id) }}" class="btn btn-sm btn-warning">
                                <i class="bi bi-pencil"></i>
                            </a>
                            <form method="POST" action="{{ url_for('{module}.delete', task_id=task.id) }}" style="display: inline;">
                                <button type="submit" class="btn btn-sm btn-danger" onclick="return confirm('Sei sicuro?')">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
        {% else %}
            <div class="alert alert-info">Nessun task trovato</div>
        {% endif %}
    </div>
</div>
{% endblock %}
"""

def write_template(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created: {path}")

# Genera template Matched Betting
write_template(f"{TEMPLATES_DIR}/matched_betting/edit.html", edit_mb_template)
write_template(f"{TEMPLATES_DIR}/matched_betting/stats.html", stats_mb_template)

# Genera template Task Lavoro
task_lavoro_index = task_index_template.format(
    title="Task Lavoro",
    icon="bi-briefcase",
    module="task_lavoro"
)
write_template(f"{TEMPLATES_DIR}/task_lavoro/index.html", task_lavoro_index)

# Genera template Task Privati
task_privati_index = task_index_template.format(
    title="Task Privati",
    icon="bi-list-check",
    module="task_privati"
)
write_template(f"{TEMPLATES_DIR}/task_privati/index.html", task_privati_index)

print("\\nTemplates generati con successo!")
print("Ora esegui questo script con: python generate_templates.py")

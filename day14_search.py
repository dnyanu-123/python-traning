{% extends "base.html" %{% block title %}Search Results — College Portal{% endblock %}

{% block content %}

<div class="d-flex justify-content-between align-items-center mb-4">
    <h2 class = "fw-bold mb-1">Search Results</h2>
    <a href = "{{url_for('students_page')}}" class = "btn btn-secondary btn-sm">
        ← All Students
        </a>
</div>

{% if query %}
<div class = "alert alert-info justify-content-between align-items-center align-items-center">
    <span>
        <strong>{{query}}</strong>
        <strong>{{students|length}}</strong> results
    </span>
    <a href = "{{url_for('search')}}" class = "btn btn-secondary btn-sm">
    Clear
    </a>
</div>
{% endif %}
<!-- Results -->


{% endblock %}


{% if students %}
<div class="card shadow-sm">
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table table-hover mb-0">
                <thead style="background-color: #1e3a5f; color:white;">
                    <tr>
                        <th class="py-3 ps-4">#</th>
                        <th class="py-3">Name</th>
                        <th class="py-3">Roll Number</th>
                        <th class="py-3">Marks</th>
                        <th class="py-3">Grade</th>
                        <th class="py-3 text-center">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for student in students %}
                    <tr class="align-middle">
                        <td class="ps-4 text-muted">
                            {{ loop.index }}
                        </td>
                        <td>
                            <div class="d-flex align-items-center">
                                <div class="rounded-circle d-flex justify-content-center align-items-center me-2"
                                     style="width:30px; height:30px; background-color:#1e3a5f; color:white;">
                                    {{ student['name'][0] }}
                                </div>
                                <span class="fw-bold">{{ student['name'] }}</span>
                            </div>
                        </td>
                        <td class="text-muted">{{ student['roll'] }}</td>
                            <td>
                                <span class="fw-bold fs-5">{{ student['marks'] }}</span>
                                <span class="text-muted small">/100</span>
                            </td>
                            <td class="text-center">
                                {% if student['marks'] >= 90 %}
                                    <span class="badge bg-success px-3 py-2">
                                        🏆 Excellent
                                    </span>
                                {% elif student['marks'] >= 75 %}
                                    <span class="badge bg-primary px-3 py-2">
                                        👍 Good
                                    </span>
                                {% elif student['marks'] >= 60 %}
                                    <span class="badge bg-warning text-dark px-3 py-2">
                                        📈 Average
                                    </span>
                                {% else %}
                                    <span class="badge bg-danger px-3 py-2">
                                        ⚠️ Needs Help
                                    </span>
                                {% endif %}
                            </td>
                            
                        </tr>
                        {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endif %} 
{% endblock %}
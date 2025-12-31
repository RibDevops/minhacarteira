## Project Description

* [live example](https://learning-zone.github.io/website-templates/simple-sidebar)

![alt text](https://github.com/learning-zone/website-templates/blob/master/assets/simple-sidebar.png "simple-sidebar")


<!-- ✅ Estrutura semântica padrão para todas as páginas -->
{% extends 'base.html' %}

{% block content %}
<article>
    <header>
        <h1>Título da Página</h1>
    </header>
    
    <section class="main-content">
        <!-- Conteúdo principal -->
    </section>
    
    <aside>
        <!-- Conteúdo secundário se houver -->
    </aside>
</article>
{% endblock %}

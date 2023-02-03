import json
from plugin.core.services.visualizer import BaseVisualizer
from django.template import engines

class SimpleVisualizer(BaseVisualizer):

    def identifier(self):
        return "simple-visualizer"

    def name(self):
        return "Simple View"

    def visualize(self, graph, request): 
        vertices = {}
        for v in graph.vertices:
            vertices[v.id] = {"id": "ID_" + str(v.id)} 

        links = []
        for e in graph.edges():
            link = {"source": e.source.id, "target": e.destination.id}
            links.append(link)
            

        view = """
        {% extends "index.html" %}
        {% block mainView %}

        <style>
        .node {
        cursor: pointer;
        color: #003b73;
        text-align: center;
        }

        .link {
        fill: none;
        stroke: #404040;
        stroke-width: 1.5px;
        }
        </style>

        <svg width="100%" height="100%" id='mainView'></svg>

        <script type="text/javascript">

        var vertices = JSON.parse("{{vertices |escapejs}}");                
        var links= JSON.parse("{{links |escapejs}}");

        links.forEach(function(link) {
            link.source = vertices[link.source];
            link.target = vertices[link.target];
        });

        var force = d3.layout.force() //kreiranje force layout-a
            .size([800, 650]) //raspoloziv prostor za iscrtavanje
            .nodes(d3.values(vertices)) //dodaj nodove
            .links(links) //dodaj linkove
            .on("tick", tick) //sta treba da se desi kada su izracunate nove pozicija elemenata
            .linkDistance(125) //razmak izmedju elemenata
            .charge(-2000)//koliko da se elementi odbijaju
            .start(); //pokreni izracunavanje pozicija
      
        var svg = d3.select('#mainView').call(d3.behavior.zoom().on("zoom", function () {
            svg.attr("transform", "translate(" + d3.event.translate + ")" + " scale(" + d3.event.scale + ")")
        })).append("g");

        // add the links
        var link = svg.selectAll('.link')
            .data(links)
            .enter().append('line')
            .attr('class', 'link');

        // add the nodes
        var node = svg.selectAll('.node')
            .data(force.nodes()) //add
            .enter().append('g')
            .attr('class', 'node')
            .attr('id', function(d){return d.id;})
            .on('click',function(){
            nodeClick(this);
            });
        d3.selectAll('.node').each(function(d){simpleView(d);});

        function simpleView(d){
            var width=32;
            var textSize=15;

            //Ubacivanje kruga
            d3.select("g#"+d.id).append('circle').
            attr('cx',0).attr('cy', 0).attr('r', width).attr('fill', '#003b73');
            //Ubacivanje naziva prodavnice ili artikla
            d3.select("g#"+d.id).append('text').attr('x', 0).attr('y', 4)
            .attr('text-anchor','middle')
            .attr('font-size',textSize).attr('font-family','poppins')
            .attr('fill','white').text(d.id);
        }

        function tick(e) {

            node.attr("transform", function(d) {return "translate(" + d.x + "," + d.y + ")";})
                .call(force.drag);

            link.attr('x1', function(d) { return d.source.x; })
                .attr('y1', function(d) { return d.source.y; })
                .attr('x2', function(d) { return d.target.x; })
                .attr('y2', function(d) { return d.target.y; });

        }
        function nodeClick(el){
            alert("ID: "+el.id);
        }


        </script>
        {% endblock %}
        """

        django_engine = engines['django']
        view_html = django_engine.from_string(view)
        view_html = view_html.render({"vertices": json.dumps(vertices), "links":json.dumps(links)}, request)
        return view_html

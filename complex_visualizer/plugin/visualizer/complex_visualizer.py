import json;

from plugin.core.services.visualizer import BaseVisualizer
from plugin.core.models import Vertex, Edge, Graph

from django.template import engines

class ComplexVisualizer(BaseVisualizer):
    def identifier(self):
        return "ComplexVisualizer"

    def name(self):
        return "Show graph with complex view"

    def visualize(self, graph, request):
        nodes = {}
        for v in graph.vertices:
            # nodes[v.id] = {"id": "id_" + str(v.id)}
            attributes = []
            for attribute_key in v.attributes.keys():
                attributes.append(attribute_key + ":" + str(v.attributes[attribute_key]))
            nodes[v.id] = {
                "id": "id_" + str(v.id),
                "attributes": attributes
            }
        links = []
        for l in graph.edges():
            link = {"source": l.source.id, "target": l.destination.id}
            links.append(link)

        view = """{% extends "index.html" %}
                    {% block mainView %}
                    <style>

                    .node {
                    cursor: pointer;
                    color: #003B73;

                    }

                    .link {
                    fill: none;
                    stroke: #9ecae1;
                    stroke-width: 1.5px;
                    }

                    </style>
                        <svg id="mainView" width="100%" height="100%">

                        </svg>
                    <script>

                    var nodesGraph = JSON.parse("{{nodes |escapejs}}");                
                    var linksGraph = JSON.parse("{{links |escapejs}}");

                    linksGraph.forEach(function(link) {
                    link.source = nodesGraph[link.source];
                    link.target = nodesGraph[link.target];
                });

                    function nodeClick(el){
                        alert("ID: "+el.id);
                        }

                        var force = d3.layout.force() //kreiranje force layout-a
                            .size([400, 400]) //raspoloziv prostor za iscrtavanje
                            .nodes(d3.values(nodesGraph)) //dodaj nodove
                            .links(linksGraph) //dodaj linkove
                            .on("tick", tick) //sta treba da se desi kada su izracunate nove pozicija elemenata
                            .linkDistance(300) //razmak izmedju elemenata
                            .charge(-100)//koliko da se elementi odbijaju
                            .start(); //pokreni izracunavanje pozicija

                        var svg=d3.select('#mainView');
                        // add the links
                        var link = svg.selectAll('.link')
                            .data(linksGraph)
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
                        d3.selectAll('.node').each(function(d){slozenPrikaz(d);});

                        function slozenPrikaz(d){
                        var length = -Infinity;
                        for(var i=0;i<d.attributes.length;i++){
                            if(length<d.attributes[i].length) length = d.attributes[i].length
                        }

                        var attributesNum = d.attributes.length;

                        var textSize = 12;
                        var visina = 30;
                        visina += (attributesNum == 0) ? textSize: attributesNum*textSize;
                        var duzina = length * textSize/2;

                        //Ubacivanje kvadrata
                        d3.select("g#"+d.id).append('rect').
                            attr('x',0).attr('y',0).attr('width',duzina).attr('height',visina)
                            .attr('fill','#003B73');
                        //Ubacivanje naziva prodavnice ili artikla
                        d3.select("g#"+d.id).append('text').attr('x',duzina/2).attr('y',10)
                         .attr('text-anchor','middle')
                         .attr('font-size',textSize).attr('font-family','Poppins')
                         .attr('fill','white').text(d.id);

                        //Ubacivanje razdelnika
                         d3.select("g#"+d.id).append('line').
                         attr('x1',0).attr('y1',textSize).attr('x2',duzina).attr('y2',textSize)
                         .attr('stroke','gray').attr('stroke-width',2);

                        // Ubacivanje teksta za kategorije
                            for(var i=0;i<attributesNum;i++)
                         {
                            
                             d3.select("g#"+d.id).append('text').attr('x',0).attr('y',20+i*textSize)
                            .attr('text-anchor','start')
                             .attr('font-size',textSize).attr('font-family','Poppins')
                             .attr('fill','white').text(d.attributes[i]);

                            }
                        }

                        function tick(e) {

                            node.attr("transform", function(d) {return "translate(" + d.x + "," + d.y + ")";})
                                .call(force.drag);

                            link.attr('x1', function(d) { return d.source.x; })
                                .attr('y1', function(d) { return d.source.y; })
                                .attr('x2', function(d) { return d.target.x; })
                                .attr('y2', function(d) { return d.target.y; });
                        }

                    </script>
                    {% endblock %}"""


        django_engine = engines['django']
        view_html = django_engine.from_string(view)
        template_html = view_html.render({"nodes": json.dumps(nodes), "links": json.dumps(links)}, request)
        return template_html
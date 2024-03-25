<template>
<v-container>
  <!-- Title and Search Bar as before -->
  <v-row class="text-center my-4">
    <v-col>
      <h1>Legal Document Network Graph</h1>
      <p class="subtitle-1">
        Explore the intricate network of connections between various legal documents. Click on a node to
        view more details about a document.
      </p>
    </v-col>
  </v-row>
  <v-row justify="center">
    <v-col cols="12" sm="8" md="6">
      <v-text-field v-model="searchQuery" label="Search Document" append-icon="mdi-magnify"
        @keyup.enter="searchDocument" outlined></v-text-field>
    </v-col>
  </v-row>
  
  <!-- Graph Container -->
  <v-row justify="center">
    <v-col cols="12">
      <div class="graph-container" style="width: 100%; height: 800px; border: 1px solid #ccc; border-radius: 8px; margin-bottom: 20px;">
        <div id="network" style="width: 100%; height: 100%;"></div>
      </div>
    </v-col>
  </v-row>
  
  <!-- Visual Legend for Node Colors and Shapes, now placed below the graph and compacted -->
  <v-row>
    <v-col cols="12">
      <v-card outlined class="mb-5">
        <v-card-title>Legend</v-card-title>
        <v-card-text>
          <div class="d-flex flex-row flex-wrap align-center justify-start">
            <div class="mr-4"><strong>Area:</strong></div>
            <div v-for="(color, area) in areaColors" :key="`area-${area}`" class="mr-2 my-1">
              <v-chip :color="color" small>{{ area }}</v-chip>
            </div>
          </div>
          <div class="d-flex flex-row flex-wrap align-center justify-start mt-3">
            <div class="mr-4"><strong>Origin:</strong></div>
            <div v-for="(format, origin) in nodeFormats" :key="`origin-${origin}`" class="mr-2 my-1">
              <v-icon small>
                {{
                  format === 'dot' ? 'mdi-circle-outline' :
                  format === 'square' ? 'mdi-checkbox-blank-outline' :
                  'mdi-triangle-outline'
                }}
              </v-icon> {{ origin }}
            </div>
          </div>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</v-container>


</template>


<script>
import { Network } from 'vis-network/standalone';
import { DataSet } from 'vis-data';
import axios from 'axios';
const apiUrl = import.meta.env.VITE_API_URL;
export default {
    name: 'NetworkGraph',
    data() {
        return {
            lastHighlightedNode: null,
            searchQuery: '',
            nodes: new DataSet([]), // Initialize nodes as a DataSet
            edges: new DataSet([]), // Initialize edges as a DataSet
            network: null,
            areaColors: {
                'Healthcare': '#37F00E', // Green
                'Emergency Services': '#145A32', // Dark Green
                'Finance': '#FFC107', // Yellow
                'e-commerce': '#7D6608 ', // Amarelo escuro
                'Energy': '#E67E22', // Deep Orange
                'Defense': '#9C27B0', // Purple
                'Cybercrime': '#D2B4DE', // Lilás
                'Justice': '#4A235A', // Roxo
                'AI': '#00BCD4', // Cyan
                'Digitalization': '#3498DB', // Azul Claro
                'Digital ID': '#001AD9', // Azul Escuro
                'Digital Rights': '#1ABC9C', // Azul Marinho
                'Agriculture': '#4C5E4C', // Verde seco
                'Telecommunications': '#EB7DFF', // rosa
                'Transport': '#F40404', // Vermelho
                'Aviation': '#F16868', // Salmon
                'Electronics': '#6E2C00 ', // Castanho
                'General': '#9E9E9E', // Cinza
            },
            nodeFormats: {
                'Portugal': 'square',
                'European Union': 'dot',
                'Other': 'triangle'
            },
        };
    },
    methods: {
        async fetchDocuments() {
            try {
                const response = await axios.get(`${apiUrl}/get-documents`);
                const documents = response.data.documents;
                this.createGraphData(documents);
            } catch (error) {
                console.error('Error fetching documents:', error);
            }
        },
        createGraphData(documents) {
    const nodesArray = documents.map(doc => {
        // Split the area on '/' to handle documents associated with two areas
        const areas = doc.area.split('/');
        let borderColor, backgroundColor;

        // Determine border and background colors based on the number of areas
        if (areas.length === 2) {
            // Document belongs to two areas
            borderColor = this.areaColors[areas[0]] || this.areaColors['Other'];
            backgroundColor = this.areaColors[areas[1]] || this.areaColors['Other'];
        } else {
            // Document belongs to one area or is uncategorized ('Other')
            borderColor = this.areaColors[doc.area] || this.areaColors['Other'];
            backgroundColor = borderColor; // Use the same color for both
        }

        return {
            id: doc._id,
            label: this.breakTextIntoMultiline(doc.title, 20), // Break title into multiple lines if needed
            title: doc.title,
            shape: this.nodeFormats[doc.origin] || this.nodeFormats['Other'], // Use document origin or default shape
            color: {
                border: borderColor,
                borderWidth: 4,
                background: backgroundColor,
                highlight: {
                    border: borderColor, 
                    background: backgroundColor,
                    borderWidth: 4 
                }
            },
        };
    });

    const edgesArray = [];
    // Map document titles to their normalized form for easy lookup
    const documentTitles = documents.reduce((acc, doc) => {
        acc[this.normalizeString(doc.title)] = doc._id;
        return acc;
    }, {});

    documents.forEach(doc => {
        if (doc.related_docs && doc.related_docs.length) {
            doc.related_docs.forEach(relatedTitle => {
                const normalizedRelatedTitle = this.normalizeString(relatedTitle);
                // Ensure the related document exists and avoid duplicate edges
                if (documentTitles[normalizedRelatedTitle] && !edgesArray.find(e => e.from === doc._id && e.to === documentTitles[normalizedRelatedTitle])) {
                    edgesArray.push({
                        from: doc._id,
                        to: documentTitles[normalizedRelatedTitle]
                    });
                }
            });
        }
    });

    // Clear existing nodes and edges and add new data
    this.nodes.clear();
    this.nodes.add(nodesArray);
    this.edges.clear();
    this.edges.add(edgesArray);

    // Build or update the graph with new nodes and edges
    this.buildGraph();
},
        buildGraph() {
            const container = document.getElementById('network');
            const data = { nodes: this.nodes, edges: this.edges };
            const options = {
                nodes: {
                    shape: 'dot', // or 'ellipse', 'circle', 'box', etc.
                    size: 16, // Adjust size of the nodes
                    font: {
                        size: 14, // Font size of labels
                        color: '#333333' // Color of labels
                    },
                    scaling: {
                        label: {
                            enabled: true,
                            min: 14,
                            max: 18,
                            maxVisible: 20,
                            drawThreshold: 5
                        }
                    },

                    color: {
                        border: '#2c3e50', // Border color of nodes
                        background: '#95a5a6', // Background color of nodes
                        highlight: {
                            border: '#34495e', // Border color when node is highlighted
                            background: '#bdc3c7' // Background color when node is highlighted
                        }
                    },
                    borderWidth: 2 // Border width of nodes
                },
                edges: {
                    color: {
                        color: '#7f8c8d', // Color of edges
                        highlight: '#16a085' // Color of edges when highlighted
                    },
                    width: 2 // Width of edges
                },
                interaction: {
                    hover: true, // Enable hover effect
                },
                layout: {
                    improvedLayout: false, // Enable improved layout algorithm
                },
                physics: {
                    enabled: true,
                    solver: 'forceAtlas2Based',
                    forceAtlas2Based: {
                        gravitationalConstant: -50,
                        centralGravity: 0.01,
                        springConstant: 0.08,
                        springLength: 100,
                        damping: 0.4,
                        avoidOverlap: 1
                    },
                },

            };
            this.network = new Network(container, data, options);
            this.network.on("stabilizationIterationsDone", () => {
                this.network.fit({
                    animation: true,
                });
            });
            // Add event listener for node clicks
            this.network.on("click", params => {
                if (params.nodes.length > 0) {
                    const nodeId = params.nodes[0]; // Get the ID of the clicked node
                    this.navigateToDocumentDetail(nodeId);
                }
            });
        },

        navigateToDocumentDetail(nodeId) {
            console.log('Navigating to document details:', nodeId);
            // Assuming this.nodes already contains the necessary details for each document
            const node = this.nodes.get(nodeId); // Use .get() if this.nodes is a DataSet
            if (node) {
                this.$router.push({ name: 'Details', params: { id: node.id } }); // Use the node id for navigation
            } else {
                console.error('Document not found.');
            }
        },
        normalizeString(str) {
            return str.toLowerCase().replace(/\s/g, '').substring(0, 25);
        },
        breakTextIntoMultiline(text, maxLineLength) {
            const words = text.split(' ');
            let line = '';
            let result = '';

            words.forEach(word => {
                if ((line + word).length > maxLineLength) {
                    result += line + '\n';
                    line = word + ' ';
                } else {
                    line += word + ' ';
                }
            });

            result += line; // Add the last line
            return result.trim();
        },
        searchDocument() {
            console.log('Searching for document:', this.searchQuery);
            const nodeId = this.getDocumentNodeIdByTitle(this.searchQuery);
            if (nodeId) {
                this.highlightNode(nodeId);
                this.network.focus(nodeId, { animation: true, scale: 1.5 });
                // Optionally highlight the node
            } else {
                console.error('Document not found.');
            }
        },
        getDocumentNodeIdByTitle(title) {
            const matchingNodes = this.nodes.get({
                filter: (node) => node.title.toLowerCase().trim().includes(title.toLowerCase().trim())
            });
            return matchingNodes.length > 0 ? matchingNodes[0].id : null;
        },
        highlightNode(nodeId) {
            // Reset the last highlighted node's style
            if (this.lastHighlightedNode) {
                this.nodes.update({
                    id: this.lastHighlightedNode,
                    borderWidth: 1, // Reset to default or initial border width
                    borderColor: '#2c3e50', // Reset to default or initial border color
                });
            }

            // Highlight the new node
            const nodeToUpdate = this.nodes.get(nodeId);
            if (nodeToUpdate) {
                this.nodes.update({
                    id: nodeId,
                    borderWidth: 4,
                    color: {
                        border: '#000000',
                        hover: {
                            border: '#000000',
                        },
                    },
                });
            }
            this.lastHighlightedNode = nodeId;
        },



    },

    mounted() {
        this.fetchDocuments();
    }
};
</script>

<style scoped>
.graph-container {
    /* Adds shadow and padding around the graph container */
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    padding: 20px;
    background-color: #fff;
    margin-top: 10px;
}
</style>
<template>
    <v-container>

        <v-row class="text-center my-4">
            <v-col>
                <h1>Legal Document Network Graph</h1>
                <p class="subtitle-1">
                    Explore the intricate network of connections between various legal documents. Click on a node to
                    view
                    more details about a document.
                </p>
            </v-col>
        </v-row>
        <v-row justify="center">
            <v-col cols="12" sm="8" md="6">
                <v-text-field v-model="searchQuery" label="Search Document" append-icon="mdi-magnify"
                    @keyup.enter="searchDocument" outlined></v-text-field>
            </v-col>
            <v-col cols="12" md="10">
                <div class="graph-container"
                    style="width: 100%; height: 800px; border: 1px solid #ccc; border-radius: 8px;">
                    <div id="network" style="width: 100%; height: 100%;"></div>
                </div>
            </v-col>
        </v-row>
    </v-container>
</template>

<script>
import { Network } from 'vis-network/standalone';
import axios from 'axios';
const apiUrl = import.meta.env.VITE_API_URL;
export default {
    name: 'NetworkGraph',
    data() {
        return {
            searchQuery: '',
            network: null,
            areaColors: {
                'Healthcare': '#8BC34A', // Green
                'Finance': '#FFC107', // Amber
                'Energy': '#FF5722', // Deep Orange
                // Add more areas and colors as needed
                'General': '#2196F3', // Blue
                'Defense': '#9C27B0', // Purple
                'AI': '#00BCD4', // Cyan
                'Other': '#9E9E9E' // Grey for documents that don't fit into any category
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
            const nodes = [];
            const edges = [];
            const documentTitles = documents.map(doc => this.normalizeString(doc.title));

            documents.forEach(doc => {
                const nodeColor = this.areaColors[doc.area] || this.areaColors['Other'];
                // Add a node for each document
                nodes.push({
                    id: doc.title, label: this.breakTextIntoMultiline(doc.title, 20), title: doc.title, group: doc.area, color: {
                        border: nodeColor,
                        background: nodeColor,
                        highlight: {
                            border: nodeColor,
                            background: nodeColor
                        }
                    }
                });

                // Add edges for related documents
                if (doc.related_docs && doc.related_docs.length) {
                    doc.related_docs.forEach(relatedTitle => {
                        const normalizedRelatedTitle = this.normalizeString(relatedTitle);
                        if (documentTitles.includes(normalizedRelatedTitle)) {
                            edges.push({ from: doc.title, to: documents.find(d => this.normalizeString(d.title) === normalizedRelatedTitle).title });
                        }
                    });
                }
            });

            this.buildGraph(nodes, edges);
        },
        buildGraph(nodes, edges) {
            const container = document.getElementById('network');
            const data = { nodes, edges };
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
            // Find the document ID by the node ID (title)
            axios.get(`${apiUrl}/get-documents`)
                .then(response => {
                    const documents = response.data.documents;
                    const doc = documents.find(d => d.title === nodeId);
                    if (doc && doc._id) {
                        this.$router.push({ name: 'Details', params: { id: doc._id } });
                    }
                })
                .catch(error => console.error('Error navigating to document detail:', error));
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
        async searchDocument() {
            if (!this.searchQuery) return;

            // Assuming you have a way to map document titles to node IDs
            const nodeId = this.getDocumentNodeIdByTitle(this.searchQuery);
            if (!nodeId) {
                console.error("Document not found.");
                return;
            }

            this.highlightNode(nodeId);
            this.network.focus(nodeId, { scale: 1.5, animation: true });
        },
        highlightNode(nodeId) {
            // Change node color or size to highlight it
            const updatedNodes = this.nodes.map(node => {
                if (node.id === nodeId) {
                    return { ...node, color: "#f00", size: 30 }; // Example: Highlight by changing color and size
                }
                return node;
            });

            // Update the nodes dataset if you're using vis Data
            this.nodes.update(updatedNodes);
        },
        getDocumentNodeIdByTitle(title) {
            // Implement this method based on how you store/manage your nodes data
            // For example, find the node ID in your nodes array that matches the title
            const matchingNode = this.nodes.get({
                filter: function (node) {
                    return node.title === title;
                }
            });

            return matchingNode.length > 0 ? matchingNode[0].id : null;
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
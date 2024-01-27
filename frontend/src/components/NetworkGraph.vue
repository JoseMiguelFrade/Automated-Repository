<template>
    <div>
        <div id="network" style="width: 100%; height: 500px;"></div>
    </div>
</template>
  
<script>
import { Network } from 'vis-network/standalone';
import axios from 'axios';
const apiUrl = import.meta.env.VITE_API_URL;
export default {
    name: 'NetworkGraph',
    data() {
        return {
            network: null,
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
                // Add a node for each document
                nodes.push({ id: doc.title, label: doc.title });

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
      improvedLayout: true, // Enable improved layout algorithm
    }
  };
            this.network = new Network(container, data, options);

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

    },
    mounted() {
        this.fetchDocuments();
    }
};
</script>
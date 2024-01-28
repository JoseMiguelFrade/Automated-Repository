<template>
    <!-- Confirmation Dialog -->
    <v-dialog v-model="dialog" max-width="400">
        <v-card>
            <v-card-title class="headline">Confirm Deletion</v-card-title>
            <v-card-text>Are you sure you want to delete this document?</v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="green darken-1" text @click="dialog = false">Cancel</v-btn>
                <v-btn color="red darken-1" text @click="confirmDeletion">Confirm</v-btn>
                <v-spacer></v-spacer>
            </v-card-actions>
        </v-card>
    </v-dialog>
    <!-- Snackbar for success message -->
    <v-snackbar v-model="snackbar.show" :timeout="3000">
        {{ snackbar.text }}
        <v-btn color="red" text @click="snackbar.show = false">
            Close
        </v-btn>
    </v-snackbar>


    <v-container>
        <v-card class="mx-auto" max-width="800">
            <v-card-title class="text-h4 text-center justify-center text-wrap">{{ documentDetails.title }}</v-card-title>
            <v-card-subtitle class="text-center justify-center mb-4 text-wrap">
                {{ documentDetails.issuer }} - {{ documentDetails.origin }} - {{ documentDetails.type }}
            </v-card-subtitle>
            <v-card-text>
                <v-list>
                    <v-list-item>
                        <v-list-item-content>
                            <v-list-item-title><strong>Subject:</strong> {{ documentDetails.subject }}</v-list-item-title>
                        </v-list-item-content>
                    </v-list-item>
                    <v-list-item>
                        <v-list-item-content>
                            <v-list-item-title><strong>Date of Issue:</strong> {{ documentDetails.date
                            }}</v-list-item-title>
                        </v-list-item-content>
                    </v-list-item>
                    <v-list-item>
                        <v-list-item-content>
                            <v-list-item-title><strong>Area:</strong> {{ documentDetails.area }}</v-list-item-title>
                        </v-list-item-content>
                    </v-list-item>
                    <v-list-item>
                        <v-list-item-content>
                            <v-list-item-title class="text-wrap">
                                <strong>Related Documents:</strong>
                                {{ documentDetails.related_docs && documentDetails.related_docs.length ?
                                    documentDetails.related_docs.join(', ') : 'None' }}
                            </v-list-item-title>
                        </v-list-item-content>
                    </v-list-item>
                    <v-list-item>
                        <v-list-item-content>
                            <v-list-item-title class="text-wrap"><strong>Abstract:</strong> {{ documentDetails.abstract
                            }}</v-list-item-title>
                        </v-list-item-content>
                    </v-list-item>
                </v-list>
            </v-card-text>
        </v-card>
    </v-container>
    <v-footer fixed padless>
        <v-container>
            <v-row justify="center">
                <v-col cols="12" sm="10" md="8" lg="6">
                    <v-toolbar color="primary" class="rounded">
                        <v-spacer></v-spacer>
                        <v-btn icon @click="Back">
                            <v-icon>mdi-arrow-left</v-icon>
                        </v-btn>
                        <v-btn icon @click="editDocument">
                            <v-icon>mdi-pencil</v-icon>
                        </v-btn>
                        <v-btn icon @click="goToRegeneratePage">
                            <v-icon>mdi-robot</v-icon>
                        </v-btn>
                        <v-btn icon @click="downloadPDF">
                            <v-icon>mdi-download</v-icon>
                        </v-btn>
                        <v-btn icon @click="deleteDocument">
                            <v-icon>mdi-delete</v-icon>
                        </v-btn>
                        <v-spacer></v-spacer>
                    </v-toolbar>
                </v-col>
            </v-row>
        </v-container>
    </v-footer>
</template>
  
<script>
import axios from 'axios';
const apiUrl = import.meta.env.VITE_API_URL;
export default {
    name: 'Details',
    data() {
        return {
            dialog: false,
            documentDetails: {},
            snackbar: { show: false, text: '' }
        }
    },
    async created() {
        const documentId = this.$route.params.id;
        try {
            const response = await axios.get(`${apiUrl}/get-document/${documentId}`);
            this.documentDetails = response.data;
        } catch (error) {
            console.error('Error fetching document details:', error);
        }
    },
    methods: {
        Back() {
            this.$router.push({ name: 'Repository' });
        },
        deleteDocument() {
            this.dialog = true; // Open the confirmation dialog
        },
        editDocument() {
            this.$router.push({ name: 'EditDocument', params: { id: this.documentDetails._id } });
        },
        async confirmDeletion() {
            try {
                await axios.delete(`${apiUrl}/delete-document/${this.documentDetails._id}`);
                // this.snackbar.text = 'Document Deleted';
                // this.snackbar.show = true;
                this.dialog = false; // Close the dialog
                this.$router.push('/repository');
            } catch (error) {
                console.error('Error deleting document:', error);
                this.snackbar.text = 'Error - Document Not Deleted';
                this.snackbar.show = true;
            }
        },
        downloadPDF() {
            const documentId = this.documentDetails._id;
            const pdfUrl = `${apiUrl}/get-pdf/${documentId}`;

            // Create a temporary link element and trigger the download
            const link = document.createElement('a');
            link.href = pdfUrl;
            link.target = '_blank';
            link.download = this.documentDetails.name + '.pdf'; // Optional: Set the download file name
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        },
        goToRegeneratePage() {
            this.$router.push({ name: 'Regenerate', params: { id: this.documentDetails._id } });
        }

    }
}
</script>
<style>
.text-wrap {
    white-space: normal !important;
}
</style>
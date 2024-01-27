<template>
    <v-container>
        <v-card class="mx-auto" max-width="800">
            <v-card-title class="text-h4">Edit Document</v-card-title>
            <v-card-text>
                <v-form ref="form" v-model="valid">
                    <v-text-field v-model="documentDetails.title" label="Name"></v-text-field>
                    <v-text-field v-model="documentDetails.issuer" label="Issuer"></v-text-field>
                    <v-text-field v-model="documentDetails.origin" label="Origin"></v-text-field>
                    <v-text-field v-model="documentDetails.type" label="Type"></v-text-field>
                    <v-text-field v-model="documentDetails.subject" label="Subject"></v-text-field>
                    <v-text-field v-model="documentDetails.date" label="Date of Issue"></v-text-field>
                    <v-text-field v-model="documentDetails.area" label="Area"></v-text-field>
                    <v-text-field label="Related Documents" v-model="editableRelatedDocs"
                        placeholder="Enter related documents separated by commas">
                    </v-text-field>
                    <v-textarea v-model="documentDetails.abstract" label="Abstract"></v-textarea>
                    <v-text-field v-model="documentDetails.pdf_path" label="PDF Path"></v-text-field>
                    <v-btn :disabled="!valid" color="primary" @click="saveDocument">Save</v-btn>
                </v-form>
            </v-card-text>
        </v-card>
    </v-container>
</template>
  
<script>
import axios from 'axios';
const apiUrl = import.meta.env.VITE_API_URL;

export default {
    data() {
        return {
            valid: true,
            documentDetails: {
                title: '',
                issuer: '',
                origin: '',
                type: '',
                subject: '',
                date: '',
                area: '',
                abstract: '',
                pdf_path: ''
            },
            editableRelatedDocs: '',
        }
    },
    async created() {
    const documentId = this.$route.params.id;
    try {
      const response = await axios.get(`${apiUrl}/get-document/${documentId}`);
      this.documentDetails = response.data;
      this.editableRelatedDocs = this.documentDetails.related_docs.join(', ');
    } catch (error) {
      console.error('Error fetching document details:', error);
    }
  },

  methods: {
    async saveDocument() {
      if (this.$refs.form.validate()) {
        // Split and trim editableRelatedDocs before sending
        this.documentDetails.related_docs = this.editableRelatedDocs.split(',').map(doc => doc.trim());

        try {
          await axios.put(`${apiUrl}/update-document/${this.documentDetails._id}`, this.documentDetails);
          this.$router.push('/repository');
        } catch (error) {
          console.error('Error updating document:', error);
        }
      }
    }
  }
}
</script>
  
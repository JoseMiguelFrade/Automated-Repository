<template>
  <v-container>
    <h1>Regenerate Document Fields</h1>
    <div class="my-4">
      <div class="text-h6">Select the creativity level:</div>
      <div class="d-flex align-center">
        <span>0 - More Technical</span>
        <v-slider v-model="creativityLevel" :min="0" :max="2" :step="0.1" thumb-label="always" class="mx-4"></v-slider>
        <span>2 - More Creative</span>
      </div>
    </div>
    <v-row>
      <template v-for="field in orderedFields" :key="field">
        <v-col cols="12">
          <div class="text-h6 my-2">{{ capitalizeFirstLetter(field) }}</div>
          <v-textarea :value="documentFields[field]" readonly outlined auto-grow></v-textarea>
          <div class="d-flex">
            <v-btn icon small @click="goBack(field)">
              <v-icon>mdi-arrow-left</v-icon>
            </v-btn>
            <v-btn icon small @click="regenerateField(field)">
              <v-icon>mdi-refresh</v-icon>
            </v-btn>
          </div>
        </v-col>
      </template>
    </v-row>
  </v-container>
  <v-footer>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" sm="10" md="8" lg="6" class="d-flex justify-center">
        <v-btn color="green darken-1" text class="mx-2" @click="save">
          Save
        </v-btn>
        <v-btn color="red darken-1" text class="mx-2" @click="cancel">
          Cancel
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</v-footer>

</template>
  
  
<script>
import axios from 'axios';
const apiUrl = import.meta.env.VITE_API_URL;

export default {
  name: 'Regenerate',
  data() {
    return {
      defaultDocumentFields: {},
      documentId: this.$route.params.id,
      documentFields: {
        title: '',
        type: '',
        abstract: '',
        issuer: '',
        origin: '',
        date: '',
        subject: '',
        area: '',
        related_docs: '',
      },
      creativityLevel: 1,
    };
  },
  mounted() {
    this.fetchDocumentDetails();
  },
  computed: {
    orderedFields() {
      const fieldOrder = ['title', 'type', 'issuer', 'origin', 'date', 'subject', 'area', 'related_docs', 'abstract'];
      return fieldOrder.filter(field => field in this.documentFields);
    }
  },
  methods: {
    fetchDocumentDetails() {
      axios.get(`${apiUrl}/get-document/${this.documentId}`)
        .then(response => {
          this.documentFields = response.data;
          this.defaultDocumentFields = JSON.parse(JSON.stringify(response.data));
        })
        .catch(error => console.error('Error fetching document details:', error));
    },

    goBack(fieldName) {
      if (this.defaultDocumentFields[fieldName] !== undefined) {
        this.documentFields[fieldName] = this.defaultDocumentFields[fieldName];
      } else {
        console.error(`Field '${fieldName}' not found in default document fields`);
      }
    },
    regenerateField(fieldName) {
      axios.post(`${apiUrl}/regenerateDoc`, {
        documentId: this.documentId,
        field: fieldName,
        temperature: this.creativityLevel
      })
        .then(response => {
          if (response.data.regeneratedText && !response.data.regeneratedText.error) {
            this.documentFields[fieldName] = response.data.regeneratedText[fieldName];
          } else {
            // Handle error or invalid response format
            console.error('Error in regeneration:', response.data.regeneratedText.error || 'Invalid response format');
          }
        })
        .catch(error => console.error('Error regenerating field:', error));
    },

    capitalizeFirstLetter(string) {
      return string.charAt(0).toUpperCase() + string.slice(1);
    },
    cancel() {
      this.$router.push({ name: 'Repository' });
    },

    save() {
      axios.put(`${apiUrl}/update-document/${this.documentId}`, this.documentFields)
        .then(response => {
          // Handle successful update
          console.log('Document updated successfully:', response.data);
          this.$router.push({ name: 'Repository' });
        })
        .catch(error => {
          // Handle error
          console.error('Error updating document:', error);
        });
    }
  },
};
</script>
<style>
.my-textarea .v-textarea__wrapper {
  min-height: 10px;
  /* Adjust this value as needed */
}
</style>
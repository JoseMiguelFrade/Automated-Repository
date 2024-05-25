<template>
  <v-container fluid>
    <!-- EUR-Lex Documents Section -->
    <v-row justify="center">
      <v-col cols="12">
        <v-card class="pa-4" outlined elevation="2">
          <v-card-title>
            <h2>EUR-Lex Documents</h2>
          </v-card-title>
          <v-card-text>
            <v-row v-if="eurlexDocuments.length > 0" dense>
              <v-col v-for="(doc, index) in eurlexDocuments" :key="index" cols="12" sm="6" md="4">
                <v-card class="mb-4" :elevation="isSelected(doc.link) ? 12 : 2" outlined>
                  <v-checkbox
                    v-model="selectedDocuments"
                    :value="{ link: doc.link, source: 'EurLex' }"
                    class="checkbox"
                    :input-value="isSelected(doc.link)"
                  ></v-checkbox>
                  <v-card-title class="headline">{{ extractTitle(doc.title) }}</v-card-title>
                  <v-card-subtitle>Publication Date: {{ formatDate(doc.publication_date) }}</v-card-subtitle>
                  <v-card-text v-if="extractDescription(doc.title)">
                    <strong>Description:</strong> {{ extractDescription(doc.title) }}
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
            <v-alert v-if="eurlexDocuments.length === 0" type="info">No EUR-Lex documents available.</v-alert>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- DRE Documents Section -->
    <v-row justify="center" class="mt-5">
      <v-col cols="12">
        <v-card class="pa-4" outlined elevation="2">
          <v-card-title>
            <h2>DRE Documents</h2>
            </v-card-title>
          <v-card-text>
            <v-row v-if="DREDocuments.length > 0" dense>
              <v-col v-for="(doc, index) in DREDocuments" :key="index" cols="12" sm="6" md="4">
                <v-card class="mb-4" :elevation="isSelected(doc.link) ? 12 : 2" outlined>
                  <v-checkbox
                    v-model="selectedDocuments"
                    :value="{ link: doc.link, source: 'DRE' }"
                    class="checkbox"
                    :input-value="isSelected(doc.link)"
                  ></v-checkbox>
                  <v-card-title class="headline">{{ doc.title }}</v-card-title>
                  <v-card-subtitle>Publication Date: {{ formatDate(doc.publication_date) }}</v-card-subtitle>
                  <v-card-text v-if="doc.description">
                    <strong>Description:</strong> {{ doc.description }}
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
            <v-alert v-if="DREDocuments.length === 0" type="info">No DRE documents available.</v-alert>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Send to Crawler Button -->
    <v-row justify="center" class="mt-5 mb-4">
      <v-col cols="12" sm="10" md="8" class="d-flex justify-center">
        <v-btn color="primary" @click="sendToCrawler">
          Send to Crawler
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios';

export default {
  name: 'NewDocuments',
  data() {
    return {
      eurlexDocuments: [],
      DREDocuments: [],
      selectedDocuments: [],
      errorMessage: '',
    };
  },
  mounted() {
    this.fetchRecentDocuments();
  },
  methods: {
    fetchRecentDocuments() {
      axios.get(`${import.meta.env.VITE_API_URL}/fetch-recent-documents`)
        .then(response => {
          console.log('Fetched documents:', response.data);
          const documents = response.data;
          this.eurlexDocuments = documents.filter(doc => doc.source === 'EurLex');
          this.DREDocuments = documents.filter(doc => doc.source === 'DRE');
          this.errorMessage = '';
        })
        .catch(error => {
          console.error('Error fetching documents:', error);
          this.errorMessage = 'Failed to fetch documents. Please try again later.';
        });
    },
    formatDate(dateString) {
      const [time, date] = dateString.split(' ');
      return date;
    },
    isSelected(link) {
      return this.selectedDocuments.some(doc => doc.link === link);
    },
    toggleSelection(link, source) {
      const docIndex = this.selectedDocuments.findIndex(doc => doc.link === link);
      if (docIndex !== -1) {
        this.selectedDocuments.splice(docIndex, 1);
      } else {
        this.selectedDocuments.push({ link, source });
      }
    },
    sendToCrawler() {
      axios.post(`${import.meta.env.VITE_API_URL}/pre-crawl`, this.selectedDocuments)
        .then(response => {
          console.log('Sent to crawler:', response.data);
          const urls = response.data.urls;
          const queryString = urls.join(';');
          this.$router.push({ name: 'Crawler', query: { urls: queryString } });
        })
        .catch(error => {
          console.error('Error sending to crawler:', error);
          this.errorMessage = 'Failed to send data to crawler. Please try again later.';
        });
    },
    extractTitle(text) {
      const match = text.match(/^(.*?Regulation.*?\/\d{4}|.*?Directive.*?\/\d{4})(.*)$/i);
      return match ? match[1] : text;
    },
    extractDescription(text) {
      const match = text.match(/^(.*?Regulation.*?\/\d{4}|.*?Directive.*?\/\d{4})(.*)$/i);
      return match ? match[2].trim() : '';
    }
  }
}
</script>

<style scoped>
.v-card-title h2 {
  margin: 0;
  font-size: 1.5em;
  font-weight: bold;
}
.v-card-title.headline {
  white-space: normal !important;
  overflow: visible !important;
  text-overflow: unset !important;
}
.checkbox {
  position: absolute;
  top: 8px;
  right: 8px;
}
.v-card {
  position: relative;
}
.mt-n2 {
  margin-top: -2px !important;
}
</style>

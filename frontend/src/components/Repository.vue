<template>
    <v-container>
    <!-- Filter Button and Search Bar -->
    <v-row justify="center">
      <v-col cols="12" sm="8" md="6">
        <v-row>
          <v-col cols="2">
            <v-btn icon @click="openDialog">
              <v-icon>mdi-cog</v-icon>
            </v-btn>
          </v-col>
          <v-col cols="10">
            <v-text-field
              v-model="searchQuery"
              label="Search Documents"
              append-icon="mdi-magnify"
              @input="() => { currentPage = 1 }"  
              outlined
            ></v-text-field>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
    <!-- Document Cards -->
    <v-row>
      <v-col v-for="document in paginatedDocuments" :key="document._id" cols="12" sm="6" md="4">
        <v-card @click="goToDetails(document._id)">
          <v-card-title>{{ document.title }}</v-card-title>
          <v-card-subtitle>{{ document.issuer }} - {{ document.origin }}</v-card-subtitle>
          <v-card-text>
            <div><strong>Type:</strong> {{ document.type }}</div>
            <div><strong>Subject:</strong> {{ document.subject }}</div>
            <div><strong>Date:</strong> {{ document.date }}</div>
            <div><strong>Area:</strong> {{ document.area }}</div>
            <div>
              <strong>Related Documents:</strong>
              {{ document.related_docs && document.related_docs.length ? document.related_docs.join(', ') : 'None' }}
            </div>
            <div><strong>Abstract:</strong> {{ truncateAbstract(document.abstract) }}</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Pagination Control -->
    <v-row justify="center">
      <v-col cols="12">
        <v-pagination v-model="currentPage" :length="totalPages" circle></v-pagination>
      </v-col>
    </v-row>

    <!-- Filter Dialog -->
    <v-dialog v-model="dialog" max-width="600px">
  <v-card>
    <v-card-title class="headline">Search Filters</v-card-title>
    <v-card-text>
      <v-row>
        <v-col cols="12">
          <v-select
            label="Type"
            v-model="tempFilters.type"
            :items="['Law', 'Directive', 'Regulation', 'Other']"
            outlined
            clearable
          ></v-select>
        </v-col>
        <v-col cols="12">
          <v-select
            label="Issuer"
            v-model="tempFilters.issuer"
            :items="['EU', 'Diário da República', 'Other']"
            outlined
            clearable
          ></v-select>
        </v-col>
        <v-col cols="12">
          <v-select
            label="Country"
            v-model="tempFilters.country"
            :items="['EU', 'Portugal', 'Other']"
            outlined
            clearable
          ></v-select>
        </v-col>
        <v-col cols="12">
          <v-select
            label="Subject"
            v-model="tempFilters.subject"
            :items="['IT', 'Cybersecurity', 'Privacy', 'Digital Rights', 'AI', 'Other']"
            outlined
            clearable
          ></v-select>
        </v-col>
        <v-col cols="12">
          <v-select
            label="Area"
            v-model="tempFilters.area"
            :items="['General', 'Defense', 'Healthcare', 'Finance', 'Energy', 'Other']"
            outlined
            clearable
          ></v-select>
        </v-col>
      </v-row>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn color="blue darken-1" text @click="dialog = false">Back</v-btn>
      <v-btn color="green darken-1" text @click="applyFilters">Apply</v-btn>
    </v-card-actions>
  </v-card>
</v-dialog>
  </v-container>
</template>

<script>
import axios from 'axios';

const apiUrl = import.meta.env.VITE_API_URL;

export default {
  name: 'Repository',
  data() {
    return {
      documents: [],
      searchQuery: '',
      currentPage: 1,
      itemsPerPage: 15,
      dialog: false,
      filters: {
        type: null,
        subject: null,
        area: null,
        issuer: null,
        origin: null
      },
      tempFilters: {
        type: null,
        subject: null,
        area: null,
        issuer: null,
        origin: null
      }
    };
  },
  computed: {
    totalPages() {
      return Math.ceil(this.filteredDocuments.length / this.itemsPerPage);
    },
    paginatedDocuments() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.filteredDocuments.slice(start, end);
    },
    filteredDocuments() {
      return this.documents.filter(doc => {
        return this.applyFiltersToDocument(doc);
      });
    },
  },
  mounted() {
    this.fetchDocuments();
  },
  methods: {
    async fetchDocuments() {
      try {
        const response = await axios.get(`${apiUrl}/get-documents`);
        this.documents = response.data.documents;
      } catch (error) {
        console.error('Error fetching documents:', error);
      }
    },
    applyFiltersToDocument(doc) {
      if (this.filters.issuer && doc.issuer.toLowerCase() !== this.filters.issuer.toLowerCase()) {
        return false;
      }
      if (this.filters.origin && doc.origin.toLowerCase() !== this.filters.origin.toLowerCase()) {
        return false;
      }
      if (this.filters.type && doc.type.toLowerCase() !== this.filters.type.toLowerCase()) {
        return false;
      }
      if (this.searchQuery && !doc.title.toLowerCase().includes(this.searchQuery.toLowerCase())) {
        return false;
      }
      if (this.filters.subject && doc.subject.toLowerCase() !== this.filters.subject.toLowerCase()) {
        return false;
      }
      if (this.filters.area && doc.area.toLowerCase() !== this.filters.area.toLowerCase()) {
        return false;
      }
      return true;
    },
    applyFilters() {
      this.filters = {...this.tempFilters};
      this.dialog = false;
    },
    openDialog() {
      this.tempFilters = {...this.filters};
      this.dialog = true;
    },
    goToDetails(id) {
      this.$router.push({ name: 'Details', params: { id } });
    },
    truncateAbstract(abstract) {
      if (abstract.length > 455) {
        return abstract.substring(0, 455) + '...';
      }
      return abstract;
    }
  }
};
</script>
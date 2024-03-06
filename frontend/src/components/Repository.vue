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
            <v-text-field v-model="searchQuery" label="Search Documents" append-icon="mdi-magnify"
              @input="() => { currentPage = 1 }" outlined></v-text-field>
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
        <v-pagination v-model="currentPage" :length="totalPages" :total-visible="7" circle></v-pagination>
      </v-col>
    </v-row>

    <!-- Filter Dialog -->
    <v-dialog v-model="dialog" max-width="600px">
      <v-card>
        <v-card-title class="headline">Search Filters and Ordering</v-card-title>
        <v-card-text>
          <v-container>
            <v-row dense>
              <v-col cols="12">
                <v-subheader>Type</v-subheader>
                <v-row>
                  <v-col v-for="typeOption in typeOptions" :key="typeOption" cols="6">
                    <v-checkbox :label="typeOption" v-model="tempFilters.type" :value="typeOption"></v-checkbox>
                  </v-col>
                </v-row>
              </v-col>

              <v-col cols="12">
                <v-subheader>Issuer</v-subheader>
                <v-row>
                  <v-col v-for="issuerOption in issuerOptions" :key="issuerOption" cols="6">
                    <v-checkbox :label="issuerOption" v-model="tempFilters.issuer" :value="issuerOption"></v-checkbox>
                  </v-col>
                </v-row>
              </v-col>

              <v-col cols="12">
                <v-subheader>Origin</v-subheader>
                <v-row>
                  <v-col v-for="originOption in originOptions" :key="originOption" cols="6">
                    <v-checkbox :label="originOption" v-model="tempFilters.origin" :value="originOption"></v-checkbox>
                  </v-col>
                </v-row>
              </v-col>

              <v-col cols="12">
                <v-subheader>Subject</v-subheader>
                <v-row>
                  <v-col v-for="subjectOption in subjectOptions" :key="subjectOption" cols="6">
                    <v-checkbox :label="subjectOption" v-model="tempFilters.subject" :value="subjectOption"></v-checkbox>
                  </v-col>
                </v-row>
              </v-col>

              <v-col cols="12">
                <v-subheader>Area</v-subheader>
                <v-row>
                  <v-col v-for="areaOption in areaOptions" :key="areaOption" cols="6">
                    <v-checkbox :label="areaOption" v-model="tempFilters.area" :value="areaOption"></v-checkbox>
                  </v-col>
                </v-row>
              </v-col>

              <v-col cols="12" class="mt-4">
                <v-divider></v-divider>
                <v-subheader class="mt-3">Order By</v-subheader>
                <v-select v-model="sortingOption" :items="sortingOptions" item-value="value" item-title="text"
                  label="Sorting" return-object></v-select>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn color="blue darken-1" text @click="dialog = false">Cancel</v-btn>
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

      typeOptions: ['Law', 'Directive', 'Regulation', 'Other'],
      issuerOptions: ['EU', 'Diário da República', 'Other'],
      originOptions: ['EU', 'Portugal', 'Other'],
      subjectOptions: ['IT', 'Cybersecurity', 'Privacy', 'Digital Rights', 'AI', 'Other'],
      areaOptions: ['General', 'Defense', 'Healthcare', 'Finance', 'Energy', 'Other'],
      documents: [],
      searchQuery: '',
      currentPage: 1,
      itemsPerPage: 15,
      dialog: false,
      filters: {
        type: [],
        subject: [],
        area: [],
        issuer: [],
        origin: []
      },
      tempFilters: {
        type: [],
        subject: [],
        area: [],
        issuer: [],
        origin: []
      },
      sortingOption: { value: 'title-asc', text: 'Title Ascending' },// default sorting option
      sortingOptions: [
        { value: 'title-asc', text: 'Title Ascending' },
        { value: 'title-desc', text: 'Title Descending' },
        { value: 'date-asc', text: 'Date Ascending' },
        { value: 'date-desc', text: 'Date Descending' },
        { value: 'area-asc', text: 'Area Ascending' },
        { value: 'area-desc', text: 'Area Descending' },
        { value: 'subject-asc', text: 'Subject Ascending' },
        { value: 'subject-desc', text: 'Subject Descending' },
      ],
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
        // First, check if the document matches the search query if one is present
        const matchesSearchQuery = this.searchQuery.trim() === '' || doc.title.toLowerCase().includes(this.searchQuery.toLowerCase());

        // Then, check if it matches the selected filters
        const matchesFilters = this.applyFiltersToDocument(doc);

        // A document must match both the search query and the filters to be included
        return matchesSearchQuery && matchesFilters;
      }).sort((a, b) => {
        switch (this.sortingOption.value) {
          case 'title-asc':
            return a.title.localeCompare(b.title);
          case 'title-desc':
            return b.title.localeCompare(a.title);
          case 'date-asc':
            return this.parseDate(a.date) - this.parseDate(b.date);
          case 'date-desc':
            return this.parseDate(b.date) - this.parseDate(a.date);
          case 'area-asc':
            return a.area.localeCompare(b.area);
          case 'area-desc':
            return b.area.localeCompare(a.area);
          case 'subject-asc':
            return a.subject.localeCompare(b.subject);
          case 'subject-desc':
            return b.subject.localeCompare(a.subject);
          default:
            return 0;
        };
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
      // Helper function to determine if a document matches the "Other" criteria for a given category
      const matchesOther = (categoryOptions, docValue, selectedFilters) => {
        const lowerCaseOptions = categoryOptions.map(option => option.toLowerCase());
        const isOtherSelected = selectedFilters.includes('Other');
        const matchesPredefinedOption = lowerCaseOptions.includes(docValue.toLowerCase());
        // If "Other" is selected but the document matches a predefined option, return false
        return isOtherSelected && !matchesPredefinedOption;
      };

      // Checks if the document matches selected filters or the "Other" criteria for each category
      const matchesType = !this.tempFilters.type.length ||
        this.tempFilters.type.some(type => type === 'Other' ? matchesOther(this.typeOptions, doc.type, this.tempFilters.type) : doc.type.toLowerCase() === type.toLowerCase());

      const matchesIssuer = !this.tempFilters.issuer.length ||
        this.tempFilters.issuer.some(issuer => issuer === 'Other' ? matchesOther(this.issuerOptions, doc.issuer, this.tempFilters.issuer) : doc.issuer.toLowerCase() === issuer.toLowerCase());

      const matchesOrigin = !this.tempFilters.origin.length ||
        this.tempFilters.origin.some(origin => origin === 'Other' ? matchesOther(this.originOptions, doc.origin, this.tempFilters.origin) : doc.origin.toLowerCase() === origin.toLowerCase());

      const matchesSubject = !this.tempFilters.subject.length || this.tempFilters.subject.some(subject => subject === 'Other' ? matchesOther(this.subjectOptions, doc.subject, this.tempFilters.subject) : doc.subject.toLowerCase() === subject.toLowerCase());

      const matchesArea = !this.tempFilters.area.length || this.tempFilters.area.some(area => area === 'Other' ? matchesOther(this.areaOptions, doc.area, this.tempFilters.area) : doc.area.toLowerCase() === area.toLowerCase());



      // Combine all match conditions. A document must satisfy all category conditions to be included.
      return matchesType && matchesIssuer && matchesOrigin && matchesSubject && matchesArea; // Add other conditions here using && operator
    },
    applyFilters() {
      this.filters = { ...this.tempFilters };
      this.dialog = false;
    },
    openDialog() {
      this.tempFilters = { ...this.filters };
      this.dialog = true;
    },
    goToDetails(id) {
      this.$router.push({ name: 'Details', params: { id } });
    },
    parseDate(dateStr) {
      const parts = dateStr.split('/');
      // Note: months are 0-based in JavaScript Date
      return new Date(parts[2], parts[1] - 1, parts[0]);
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
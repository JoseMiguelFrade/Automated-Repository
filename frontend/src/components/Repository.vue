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
import { mapState, mapMutations } from 'vuex';

const apiUrl = import.meta.env.VITE_API_URL;

export default {
  name: 'Repository',
  data() {
    return {
      documents: [], // All fetched documents
      typeOptions: ['Law', 'Directive', 'Regulation', 'Technical Guide','Other'],
      issuerOptions: ['ENISA', 'Centro Nacional de Cibersegurança', 'Diário da República', 'Other'],
      originOptions: ['EU', 'European Commission','Portugal', 'Other'],
      subjectOptions: ['Cybersecurity', 'Data Privacy', 'Governance', 'Other'],
      areaOptions: ['General', 'Defense', 'Healthcare', 'Finance', 'Energy', 'Cybersecurity','AI','Transport','Digital Rights','Justice','Other'],
      documents: [],
      searchQuery: '',
      //currentPage: 1,
      itemsPerPage: 15,
      dialog: false,
      // filters: {
      //   type: [],
      //   subject: [],
      //   area: [],
      //   issuer: [],
      //   origin: []
      // },
      tempFilters: {
        type: [],
        subject: [],
        area: [],
        issuer: [],
        origin: []
      },
      //sortingOption: { value: 'title-asc', text: 'Title Ascending' },// default sorting option
      sortingOptions: [
        { value: 'title-asc', text: 'Title Ascending' },
        { value: 'title-desc', text: 'Title Descending' },
        { value: 'date-asc', text: 'Date Ascending' },
        { value: 'date-desc', text: 'Date Descending' },
        {value: 'uploaded-date-asc', text: 'Uploaded Date Ascending'},
        {value: 'uploaded-date-desc', text: 'Uploaded Date Descending'},
        { value: 'area-asc', text: 'Area Ascending' },
        { value: 'area-desc', text: 'Area Descending' },
        { value: 'subject-asc', text: 'Subject Ascending' },
        { value: 'subject-desc', text: 'Subject Descending' },
      ],
    issuerAliases: {
      'ENISA': ['ENISA', 'European Union Agency for Cybersecurity (ENISA)', 'European Union Agency For Network And Information Security (ENISA)', 'EU Cybersecurity Agency', 'European Union Agency for Network and Information Security (ENISA)'],
      'Centro Nacional de Cibersegurança': ['Centro Nacional de Cibersegurança', 'CNCS']
      
    }
    };
  },
  computed: {
    filters: {
    get() {
      // Getter: Return the filters object from Vuex state
      return this.$store.state.filters;
    },
    set(value) {
      // Setter: Commit a mutation to update filters in the Vuex store
      this.$store.commit('setFilters', value);
    }
  },

    currentPage: {
    get() {
      return this.$store.state.currentPage;
    },
    set(value) {
      this.$store.commit('setCurrentPage', value);
    }
  },
  sortingOption: {
    get() {
      return this.$store.state.sortingOption;
    },
    set(value) {
      this.$store.commit('setSortingOption', value);
    }
  
  },

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
          case 'uploaded-date-asc':
            return this.parseDateUpload(a.upload_date) - this.parseDateUpload(b.upload_date);
          case 'uploaded-date-desc':
            return this.parseDateUpload(b.upload_date) - this.parseDateUpload(a.upload_date);	          
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
    this.setCurrentPage(this.currentPage);
    this.setFilters(this.filters);
    this.setSortingOption(this.sortingOption);
  },
  methods: {
  ...mapMutations(['setCurrentPage', 'setFilters', 'setSortingOption']),
  
  async fetchDocuments() {
    try {
      const response = await axios.get(`${apiUrl}/get-documents`);
      this.documents = response.data.documents;
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  },

  applyFiltersToDocument(doc) {
    const matchesOther = (categoryOptions, docValues, selectedFilters) => {
      const lowerCaseOptions = categoryOptions.map(option => option);
      const docValuesArray = typeof docValues === 'string' ? docValues.split('/') : [docValues];
      const isOtherSelected = selectedFilters.includes('Other');
      const matchesPredefinedOption = docValuesArray.some(docValue => lowerCaseOptions.includes(docValue));
      return isOtherSelected && !matchesPredefinedOption;
    };

    const docAreas = typeof doc.area === 'string' ? doc.area.split('/') : [doc.area];
    const docSubjects = typeof doc.subject === 'string' ? doc.subject.split('/') : [doc.subject];

    const matchesCategory = (docCategories, filterCategories, categoryOptions) => {
      return !filterCategories.length || filterCategories.some(filterCategory => 
        docCategories.some(docCategory => 
          filterCategory === 'Other' ? matchesOther(categoryOptions, docCategory, filterCategories) : docCategory === filterCategory));
    };

    const matchesSingleCategory = (docCategory, filterCategory, categoryOptions) => {
      return !filterCategory.length || filterCategory.some(filter => 
        filter === 'Other' ? matchesOther(categoryOptions, docCategory, filterCategory) : docCategory === filter
      );
    };

    const matchesType = matchesSingleCategory(doc.type, this.filters.type, this.typeOptions);
    const matchesIssuer = this.matchesIssuerAlias(doc.issuer, this.filters.issuer);
    const matchesOrigin = matchesSingleCategory(doc.origin, this.filters.origin, this.originOptions);
    const matchesSubject = matchesCategory(docSubjects, this.filters.subject, this.subjectOptions);
    const matchesArea = matchesCategory(docAreas, this.filters.area, this.areaOptions);

    return matchesType && matchesIssuer && matchesOrigin && matchesSubject && matchesArea;
  },

  matchesIssuerAlias(issuer, filterIssuers) {
    if (!filterIssuers.length) return true; // If no filter is applied, return true

    const isOtherSelected = filterIssuers.includes('Other');

    if (isOtherSelected) {
      // Check if the issuer matches any of the predefined aliases
      for (const primaryIssuer in this.issuerAliases) {
        const aliasList = this.issuerAliases[primaryIssuer];
        if (aliasList.includes(issuer)) {
          return false; // Exclude documents that match any predefined alias
        }
      }
      return true; // Include documents that do not match any predefined alias
    } else {
      // Check if the issuer matches any of the selected filter issuers or their aliases
      for (const primaryIssuer of filterIssuers) {
        if (this.issuerAliases[primaryIssuer]) {
          const aliasList = this.issuerAliases[primaryIssuer];
          if (aliasList.includes(issuer)) {
            return true;
          }
        }
      }
      return filterIssuers.includes(issuer);
    }
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
    return new Date(parts[2], parts[1] - 1, parts[0]);
  },
  parseDateUpload(dateStr) {
    const parts = dateStr.split(' ');
    const date = parts[1].split('/');
    const time = parts[0].split(':');
    return new Date(date[2], date[1] - 1, date[0], time[0], time[1], time[2]);
  },
  truncateAbstract(abstract) {
    if (abstract.length > 455) {
      return abstract.substring(0, 455) + '...';
    }
    return abstract;
  }
},
  watch: {

    currentPage: {
      handler(value) {
        this.setCurrentPage(value);
      },
      immediate: true,
    },
    filters: {
      handler(value) {
        //console.log(value);
        this.setFilters(value);
      },
      deep: true,
      immediate: true,
    },
    sortingOption: {
      handler(value) {
        this.setSortingOption(value);
      },
      immediate: true,
    },
  }
};
</script>
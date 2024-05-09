<template>
    <v-container>
      <!-- Grid layout for organized fields -->
      <v-row class="mb-4">
        <v-col cols="12" sm="6">
          <v-text-field
            v-model="totalQueries"
            label="Total Queries"
            type="number"
            outlined
            dense
            hint="Enter the total number of queries to perform"
            persistent-hint
          ></v-text-field>
        </v-col>
        <v-col cols="12" sm="6">
          <v-text-field
            v-model="gpt35Count"
            label="Low-Cost Queries"
            type="number"
            outlined
            dense
            hint="Number of queries using the lower-cost GPT-3.5 Turbo model"
            persistent-hint
          ></v-text-field>
        </v-col>
      </v-row>
  
      <v-row>
        <v-col cols="12">
          <v-select
            :items="subdirectories"
            label="Select a Subdirectory for Analysis"
            v-model="selectedSubdir"
            outlined
            dense
            item-text="name"
            item-value="value"
            no-data-text="No subdirectories available"
            return-object
          ></v-select>
        </v-col>
      </v-row>
  
      <v-row>
        <v-col class="text-center">
          <v-btn color="primary" @click="updateRepo" large depressed>
            <v-icon left>mdi-update</v-icon>
            Update Repository
          </v-btn>
        </v-col>
      </v-row>
    </v-container>
  </template>
<script>
import axios from 'axios';
const apiUrl = import.meta.env.VITE_API_URL;
export default {
    name: 'Update',
  data() {
    return {
      subdirectories: [],
      selectedSubdir: '',
      totalQueries: 10,
      gpt35Count: 4,
    };
  },
  mounted() {
    this.fetchSubdirectories();
  },
  methods: {
    fetchSubdirectories() {
      axios.get(`${apiUrl}/list-subdirs`)
        .then(response => {
          this.subdirectories = response.data;
        })
        .catch(error => {
          console.error('Error fetching subdirectories:', error);
        });
    },
    updateRepo() {
      if (!this.selectedSubdir) {
        alert('Please select a subdirectory.');
        return;
      }
      if (this.totalQueries < 1) {
        alert('Please enter a valid number of total queries.');
        return;
      }
        if (this.gpt35Count < 0 || this.gpt35Count > this.totalQueries) {
            alert('Please enter a valid number of low-cost queries.');
            return;
        }

      axios.post(`${apiUrl}/update-repo`, { subdir: this.selectedSubdir, total_queries: this.totalQueries, gpt_3_5_count: this.gpt35Count })
        .then(response => {
          console.log('Repository updated successfully:', response.data);
        })
        .catch(error => {
          console.error('Error updating repository:', error);
        });
    }
  }
}
</script>

<style>
/* Your component styles here */
</style>    
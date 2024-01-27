<template>
  <div class="text-center mt-5">
    <v-row justify="center" class="mb-2" v-for="button in buttons" :key="button.text">
      <v-col cols="12" sm="6" md="4">
        <v-btn :color="button.color" small width="8cm" :prepend-icon="button.icon" @click="buttonClicked(button.action)">
          {{ button.text }}
        </v-btn>
      </v-col>
    </v-row>
    <input type="file" ref="fileInput" style="display: none" @change="handleFileUpload" />
  </div>
</template>

<script>
import axios from 'axios';
const apiUrl = import.meta.env.VITE_API_URL;
export default {
  name: 'CrawlerMenu Copy',
  data() {
    return {
      buttons: [
      { icon: 'mdi-cog', text: 'Start Crawler', color: 'primary', action: 'startCrawler' },
      { icon: 'mdi-plus-circle', text: 'Load File', color: 'primary', action: 'selectFile' }
        // ... other buttons
      ]
    };
  },
  methods: {
    buttonClicked(action) {
      if (action === 'selectFile') {
        this.selectFile();
      }
      else if (action === 'startCrawler') {
        this.startCrawler();
      }
      // Handle other actions
    },
    selectFile() {
      this.$refs.fileInput.click();
    },
    async handleFileUpload(event) {
      try {
        const file = event.target.files[0];
        if (!file) {
          return;
        }
        const formData = new FormData();
        formData.append('file', file);

        const response = await axios.post(`${apiUrl}/upload`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        console.log('File uploaded', response.data);
      } catch (error) {
        console.error('Error uploading file', error);
      }
    },
    async startCrawler() {
      try {
        const response = await axios.get(`${apiUrl}/start`);
      } catch (error) {
        console.error('Error starting crawler', error);
      }
    }
  }
}
</script> 

<style scoped>


</style>

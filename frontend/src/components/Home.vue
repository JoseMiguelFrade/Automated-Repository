<template>
 <v-container fluid class="home-container">
    <!-- Welcome Section -->
    <v-row justify="center" class="my-12">
      <v-col cols="12" sm="8" md="6" class="text-center">
        <h1 class="display-2 mb-4">Welcome to <span class="highlight">Automated Repository</span></h1>
        <p class="subtitle-1 mb-6">
          Your gateway to the world of cyberspace legal and technical documentation.
        </p>
        <v-btn large color="secondary" :to="{ name: 'Repository' }">Explore Repository</v-btn>
      </v-col>
    </v-row>
    <!-- Features Section -->
    <v-container>
      <v-row justify="center" class="my-12">
        <v-col cols="12" sm="6" md="3" class="text-center">
          <v-icon large color="primary">mdi-database-search</v-icon>
          <h2 class="title">Document Repository</h2>
          <p>Access a comprehensive collection of legal documents on cybersecurity and digital rights.</p>
        </v-col>
        <v-col cols="12" sm="6" md="3" class="text-center">
          <v-icon large color="primary">mdi-robot</v-icon>
          <h2 class="title">AI Analysis</h2>
          <p>Leverage advanced AI to analyze and gain insights from legal texts and documents.</p>
        </v-col>
        <v-col cols="12" sm="6" md="3" class="text-center">
          <v-icon large color="primary">mdi-chart-bell-curve</v-icon>
          <h2 class="title">Relation Graph</h2>
          <p>Visualize the connections and relationships between different legal documents in the database.</p>
        </v-col>
        <v-col cols="12" sm="6" md="3" class="text-center">
          <v-icon large color="primary">mdi-magnify</v-icon>
          <h2 class="title">New Documents Updates</h2>
          <p>Stay informed about the latest documents with an updated feed from major document repositories.</p>
        </v-col>
      </v-row>
    </v-container>
<!-- Footer -->
    <v-footer class="mt-auto" padless>
    <v-container fluid>
      <v-row justify="center">
        <v-col cols="12" class="text-center py-3">
          <p class="caption mb-0">
            &copy; 2024 Automated Repository is part of a thesis made for 
            <a href="https://www.ipleiria.pt" target="_blank" class="footer-link">IPLeiria</a>
          </p>
        </v-col>
      </v-row>
    </v-container>
  </v-footer>
  </v-container>
</template>

<script>
export default {
  name: 'Home',
};
</script>

<style>
.home-container {
  min-height: 100vh; /* Ensure the container takes up the full height */
  display: flex;
  flex-direction: column;
}

.highlight {
  color: #1976D2; /* Highlight color for the word 'Cyberlaw' */
  font-weight: bold;
}

.footer-link {
  color: #1976D2;
  text-decoration: none;

  &:hover {
    text-decoration: underline;
  }
}
</style>
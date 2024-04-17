import { createStore } from 'vuex'
import VuexPersist from 'vuex-persist'

const vuexPersist = new VuexPersist({
    key: 'Cyberlaw',
    storage: window.localStorage
  })

export default createStore({
    plugins: [vuexPersist.plugin],
  state() {
    return {
      currentPage: 1,
      filters: {
        type: [],
        subject: [],
        area: [],
        issuer: [],
        origin: []
      },
      sortingOption: { value: 'title-asc', text: 'Title Ascending' }
    }
  },
  mutations: {
    setCurrentPage(state, page) {
      state.currentPage = page;
    },
    setFilters(state, filters) {
      state.filters = filters;
    },
    setSortingOption(state, sortingOption) {
      state.sortingOption = sortingOption;
    }
  },
  actions: {
    updateCurrentPage({ commit }, page) {
      commit('setCurrentPage', page);
    },
    updateFilters({ commit }, filters) {
      commit('setFilters', filters);
    },
    updateSortingOption({ commit }, sortingOption) {
      commit('setSortingOption', sortingOption);
    }
  }
})
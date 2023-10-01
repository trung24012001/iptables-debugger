import ky from "ky";

const api = ky.extend({
  hooks: {
    beforeRequest: [
      async (request) => {},
    ],
    afterResponse: [
      (_request, _options, response) => {
        return response;
      },
    ],
  },
});
export default api;

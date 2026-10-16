module.exports = {
  queryRewrite: (query, { securityContext }) => {
    const country = securityContext && securityContext.country;
    if (country) {
      query.filters = query.filters || [];
      query.filters.push({
        member: "sales.users_country",
        operator: "equals",
        values: [country],
      });
    }
    return query;
  },
};

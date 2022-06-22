exports.handler = async (event) => {
    const response = {
        statusCode: 200,
        body: JSON.stringify('Application under development. Search functionality will be implemented in Assignment 3'),
    };
    return response;
};
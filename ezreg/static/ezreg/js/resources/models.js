var transformDjangoRestResponse = function(data, headers){
	try {
        var jsonObject = JSON.parse(data); // verify that json is valid
        return jsonObject.results;
    }
    catch (e) {
        console.log("did not receive a valid Json: " + e)
    }
    return {};
}
var setErrors = function(data, headers){
	console.log(data);
	return data;
//	try {
//        var jsonObject = JSON.parse(data); // verify that json is valid
//        return jsonObject.results;
//    }
//    catch (e) {
//        console.log("did not receive a valid Json: " + e)
//    }
//    return {};
}
angular.module('ezregModels', ['ngResource'])
.factory('Price', ['$resource', function ($resource) {
  return $resource('/api/prices/:id/', {id:'@id'}, {
    query: { method: 'GET', isArray:true }, //, transformResponse:transformDjangoRestResponse
    save : { method : 'PUT'},
    create : { method : 'POST'},
    remove : { method : 'DELETE' }
  });
}])
;


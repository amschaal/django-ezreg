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
.factory('Price', ['$resource','$filter', function ($resource,$filter) {
	var transform = function(obj) {
		//angular bootstrap ui tries to pass different date format to model.  Override it.
		try{
			obj.start_date = $filter('date')(obj.start_date,'yyyy-MM-dd');
		}catch(e){};
		try{
			obj.end_date = $filter('date')(obj.end_date,'yyyy-MM-dd');
		}catch(e){};
		return angular.toJson(obj);
	};
  return $resource('/api/prices/:id/', {id:'@id'}, {
    query: { method: 'GET', isArray:true }, //, transformResponse:transformDjangoRestResponse
    save : { method : 'PUT',transformRequest:transform},
    create : { method : 'POST',transformRequest:transform},
    remove : { method : 'DELETE' }
  });
}])
.factory('EventPage', ['$resource', function ($resource) {
  return $resource('/api/event_pages/:id/', {id:'@id'}, {
    query: { method: 'GET', isArray:true }, //, transformResponse:transformDjangoRestResponse
    save : { method : 'PUT'},
    create : { method : 'POST'},
    remove : { method : 'DELETE' }
  });
}])
.factory('PaymentProcessor', ['$resource', function ($resource) {
  return $resource('/api/payment_processors/:id/', {id:'@id'}, {
    query: { method: 'GET', isArray:true }, //, transformResponse:transformDjangoRestResponse
//    save : { method : 'PUT'},
//    create : { method : 'POST'},
//    remove : { method : 'DELETE' }
  });
}])

;


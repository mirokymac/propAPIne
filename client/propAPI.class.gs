/**
 * @OnlyCurrentDoc
 */
// change log:
// 2019-11-26: bug fixes for predifined bundles
//             lowercase can be use as input and out put type now
// 2024-03-06: add multi output support for propsi

(function(root){
  function ALprop(){
    if (!(this instanceof ALprop)){
      return new ALprop();
    }
  };
  
  const BASEURL = "http://localhost:22001"
  const RETRIES_MAX = 5;
  const HAPROPS = ['T', 'B', 'D', 'V', 'Vha', 'R', 'W', 'Y', 'H', 'Hha', 'S', 'Sha', 'C', 'Cha', 'M', 'Z', 'K', 'A'];
  const HAPROPS_IN = ['T', 'R', 'D', 'W', 'P', 'B', 'H', 'Hha', 'Y', 'P_w', 'S', 'Sha', 'V', 'Vha'];
  
  var PROPSI = ["DELTA", "DMOLAR", "D", "HMOLAR", "H", "P", "Q", "SMOLAR", "S", "TAU", "T", "UMOLAR", "U", "ACENTRIC", "ALPHA0", "ALPHAR", "A", "BVIRIAL", "CONDUCTIVITY", "CP0MASS", "CP0MOLAR", "CPMOLAR", "CVIRIAL", "CVMASS", "CVMOLAR", "CP", "DALPHA0_DDELTA_CONSTTAU", "DALPHA0_DTAU_CONSTDELTA", "DALPHAR_DDELTA_CONSTTAU", "DALPHAR_DTAU_CONSTDELTA", "DBVIRIAL_DT", "DCVIRIAL_DT", "DIPOLE_MOMENT", "FH", "FRACTION_MAX", "FRACTION_MIN", "FUNDAMENTAL_DERIVATIVE_OF_GAS_DYNAMICS", "GAS_CONSTANT", "GMOLAR", "GWP100", "GWP20", "GWP500", "G", "HELMHOLTZMASS", "HELMHOLTZMOLAR", "HH", "ISBRCOEFF", "ISTHCOEFF", "I", "M", "ODP", "PCRIT", "PHASE", "PH", "PIP", "PMAX", "PMIN", "PRANDTL", "PTRIPLE", "P_REDUCING", "RHOCRIT", "RHOMASS_REDUCING", "RHOMOLAR_CRITICAL", "RHOMOLAR_REDUCING", "SMOLAR_RESIDUAL", "TCRIT", "TMAX", "TMIN", "TTRIPLE", "T_FREEZE", "T_REDUCING", "V", "Z"];
  const PROPSI_QC = ["ACENTRIC", "DIPOLE_MOMENT", "FH", "FRACTION_MAX", "FRACTION_MIN", "GAS_CONSTANT", "GWP100", "GWP20", "GWP500", "HH", "M", "ODP", "PCRIT", "PH", "PMAX", "PMIN", "PTRIPLE", "P_REDUCING", "RHOCRIT", "RHOMASS_REDUCING", "RHOMOLAR_CRITICAL", "RHOMOLAR_REDUCING", "TCRIT", "TMAX", "TMIN", "TTRIPLE", "T_FREEZE", "T_REDUCING", "CRIT"];
  const PROPSI_IN = ["DMOLAR", "D", "HMOLAR", "H", "P", "Q", "SMOLAR", "S", "T", "UMOLAR", "U"];
  const regex = /[\"\'\{\}]/gi;
  const TYPE_PATTERN = /[A-Za-z0-9\_]+/gi;
  
  // predifined bundles:
  const PD_BUNDLES = {
    "HEAT": ["S", "CP", "U", "H"],
    "FLOW": ["D", "M", "V", "Z"],
    "CRIT": ["TCRIT", "PCRIT", "ACENTRIC", "M"]
  };
  PROPSI = PROPSI.concat(Object.keys(PD_BUNDLES));
  // phase fraction codes
  const PHASE_FRAC = ["VAPFRAC", "LIQFRAC"];
  const PHASE_PROP = ["FUGACITY", "FUGACITYCOEFF", "K"];
  PROPSI = PROPSI.concat(PHASE_FRAC);
  PROPSI = PROPSI.concat(PHASE_PROP);
  
  ALprop.prototype = {
    "_getBaseUrl": function(){
      if (typeof BASEURL == "string"){
        return BASEURL;
      }
      if (BASEURL instanceof Array){
        return BASEURL[Math.floor(Math.random() * BASEURL.length)];
      }
      return "http://la01.localhost:22001";
    },
    
    "_UrlCombine": function(base_url, payload){
      var fullUrl = base_url + "?"
      for (key in payload){
        if (fullUrl[fullUrl.length - 1] != "?"){
          fullUrl += "&";
        }
        fullUrl += (key + "=" + payload[key]);
      }
      return fullUrl;
    },
    
    "_isSuperSet": function(set, subset) {
      for (key in subset) {
        if (!(set.indexOf(subset[key]) > -1)) {
          return false;
        }
      }
      return true;
    },
    
    "_toSet": function(array){
      res = [];
      for (key in array){
        if (!(res.indexOf(array[key]) > -1)){
          res.push(array[key]);
        }
      };
      return res;
    },
    
    "_toResultList": function(dict, res, skips, constraints_orders){
      if (typeof skips == "string"){
        skips = [skips];
      } else if (!(skips instanceof Array)){
        skips = [];
      }
      if (!res){
        var res = [[], []];
      }
      var keys = Object.keys(dict).sort()
      var key;
      var multikeys = [];
      if (typeof dict == "object"){
        for (var i in keys){
          key = keys[i];
          if (!(skips.indexOf(key) > -1)){
            res[0].push(key);
            res[1].push(dict[key]);
            if (Array.isArray(dict[key])){
              multikeys.push(i);
            }
          }
        }
      }
      
      if (res[0].length > 1){
        for (i in multikeys){
          Logger.log(res[1][multikeys[i]])
          res[1][multikeys[i]] = res[1][multikeys[i]].join(",");
        }
      }
      if (Array.isArray(constraints_orders)){
      var k_index = 0, temp;

        for (var i in constraints_orders){
          key = constraints_orders[i];
          k_index = res[0].indexOf(key);
          if (k_index > -1){
            temp = res[0][k_index];
            res[0].splice(k_index, 1);
            res[0].push(temp);
            temp = res[1][k_index];
            res[1].splice(k_index, 1);
            res[1].push(temp);
          }
        }
      }

      if (res[0].length == 1 && Array.isArray(res[1][0])){
        i = 0;
        while (i < res[1][0].length -1){
          res[0].push("");
          i = i + 1
        }
        res[1] = res[1][0];
      }
      return res;
    },
    
    
    "haprop": function(outType, inType1, inValue1, inType2, inValue2, inType3, inValue3){
      // check input values are NUMBER
      if (!(typeof inValue1 == 'number')){
        throw new Error("inValue1 shall be a number.");
        return null;
      }
      if (!(typeof inValue2 == 'number')){
        throw new Error("inValue2 shall be a number.");
        return null;
      }
      if (!(typeof inValue3 == 'number')){
        throw new Error("inValue3 shall be a number.");
        return null;
      }
      
      // check output validation
      //outType = outType.toUpperCase();
      if (!(HAPROPS.indexOf(outType) > -1)){
        throw new Error("OutType not in list, check TypeReference");
        return null;
      }
      // check input validation
      inType1 = inType1.toUpperCase();
      inType2 = inType2.toUpperCase();
      inType3 = inType3.toUpperCase();
      var inSet = this._toSet([inType1, inType2, inType3]);
      if (inSet.length != 3 || !this._isSuperSet(HAPROPS_IN, inSet)){
        throw new Error("InType must be 3 difference kinds, check TypeReference");
        return null;
      };
      
      
      // check validation of Relative Humidity
      if (inType1 === "R"){
        if (inValue1 > 1){
          inValue1 = inValue1 / 100.0;
        }
      }
      if (inType2 === "R"){
        if (inValue2 > 1){
          inValue2 = inValue2 / 100.0;
        }
      }
      if (inType3 === "R"){
        if (inValue3 > 1){
          inValue3 = inValue3 / 100.0;
        }
      }
      
      var retries = 0;
      var response = null;
      var doneFlag = false;
      var payload = {
        'output_type': outType,
        'intype1': inType1,
        'invalue1': inValue1,
        'intype2': inType2,
        'invalue2': inValue2,
        'intype3': inType3,
        'invalue3': inValue3
      }
      while (retries < RETRIES_MAX){
        retries += 1;
        try{
          response = UrlFetchApp.fetch(
            this._UrlCombine(
              this._getBaseUrl() + "/haprop",
              payload
            )
          );
          if (response.getResponseCode() === 200){
            doneFlag = true;
            break;
          }
        } catch(err){
//          Logger.log(retries + " times Fetch Error for " + payload);
        }
      }
      if (!doneFlag){
        throw new Error("Check your input, like Pressure, which likely to have typo error.\nOr target Server can not be access, try later.");
        return null;
      }
      
      var data = JSON.parse(response)['result'];
      var res = [[], []]
      if (data){
        if (data['error']){
          throw new Error("Error occur: " + data['message']);
          return null;
        }
        if (data['warning']){
          res[0].push('warning');
          res[1].push(data['message']);
        }
      }
      res = this._toResultList(data, res, ['warning', 'error', 'message'])
      
      return res;
    },
    
    
    "propsi": function(substance, outType, inType1, inValue1, inType2, inValue2, backend){
      
      // check output validation
      outType = outType.toUpperCase();
      outType = [...outType.matchAll(TYPE_PATTERN)];
      if (outType.length > 0){
        outType = outType.map(x => x[0]);
      }
      outType = [...new Set(outType)];
      if (!this._isSuperSet(PROPSI, outType)){
        throw new Error("OutType not in list, check PropSI_NameOfTheProperties for reference");
        return null;
      }
      
      if (!backend){
        backend = "REFPROP";
      }
      // buildup the extra key-value
      var extra = {"backend": backend};
      extra = JSON.stringify(extra).replace(regex, "");
      
      var payload = null;
      var res = [[], []];
      // check input validation
      if (outType.length == 1 && !(PROPSI_QC.indexOf(outType[0]) > -1)){
        inType1 = inType1.toUpperCase();
        inType2 = inType2.toUpperCase();
        var inSet = this._toSet([inType1, inType2]);
        if (inSet.length != 2 || !this._isSuperSet(PROPSI_IN, inSet)){
          throw new Error("InType must be 2 difference kinds, check TypeReference");
          return null;
        };

        // check input values are NUMBER
        if (!(typeof inValue1 == 'number')){
          throw new Error("inValue1 shall be a number.");
          return null;
        }
        if (!(typeof inValue2 == 'number')){
          throw new Error("inValue2 shall be a number.");
          return null;
        }

        var key = outType.indexOf(inType1);
        if (key > -1){
            res[0].push(inType1);
            res[1].push(inValue1);
            outType.splice(key, 1);
        }
        
        key = outType.indexOf(inType2);
        if (outType.indexOf(inType2) > -1){
            res[0].push(inType2);
            res[1].push(inValue2);
            outType.splice(key, 1);
        }

        if (outType.length == res[0].length){
          return res
        }
        
        payload = {
          'substance': substance,
          'output_type': outType,
          'intype1': inType1,
          'invalue1': inValue1,
          'intype2': inType2,
          'invalue2': inValue2,
          'extra': extra
        }
      }
      else {
        payload = {
          'substance': substance,
          'output_type': outType,
          'intype1': 'T',
          'invalue1': '273.15',
          'intype2': 'P',
          'invalue2': '101325',
          'extra': extra
        }
      }
      
      var retries = 0;
      var response = null;
      var doneFlag = false;
//      var logtimeS = (new Date()).getTime();
      while (retries < RETRIES_MAX){
        retries += 1;
//        Logger.log(this._UrlCombine(this._getBaseUrl() + "/propsi",payload));
        try{
          response = UrlFetchApp.fetch(
            this._UrlCombine(
              this._getBaseUrl() + "/propsi",
              payload
            )
          );
          if (response.getResponseCode() === 200){
            doneFlag = true;
            break;
          }
        }
        catch(err){
          Logger.log(retries + " times Fetch Error for " + payload);
        }
      }
//      Logger.log((new Date()).getTime() - logtimeS);
      if (!doneFlag){
        throw new Error("Target Server can not be access, edit your BASEURL list.");
        return null;
      }
      
      var data = JSON.parse(response)['result'];
      var cons = [];
      if (data){
        if (data['error']){
          if (data['message']) throw new Error("Error occur: " + data['message']);
          if (data['substance']) throw new Error('Not supported substance, check SUBSTANCE_REF for supported substances');
          return null;
        }
        for (var key in PD_BUNDLES){
          if (outType.indexOf(key) > -1){
            cons = cons.concat(PD_BUNDLES[key]);
          }
        }
        res = this._toResultList(data, res, ['warning', 'error', 'message', 'substance'], cons);
        // if (extflag){
        //   res[1] = res[1][0];
        // }
        if (data['warning']){
          res[0].push('warning');
          res[1].push(data['message']);
        }
      }
      return res;
    },

    "flash": function(substance, inType1, inValue1, inType2, inValue2, backend){
      
      if (!backend){
        backend = "REFPROP";
      }
      // buildup the extra key-value
      var extra = {"backend": backend};
      extra = JSON.stringify(extra).replace(regex, "");
      
      var payload = null;
      // check input validation
      var inSet = this._toSet([inType1, inType2]);
      if (inSet.length != 2 || !this._isSuperSet(PROPSI_IN, inSet)){
        throw new Error("InType must be 2 difference kinds, check TypeReference");
        return null;
      };
      
      // check input values are NUMBER
      if (!(typeof inValue1 == 'number')){
        throw new Error("inValue1 shall be a number.");
        return null;
      }
      if (!(typeof inValue2 == 'number')){
        throw new Error("inValue2 shall be a number.");
        return null;
      }
      
      payload = {
        'substance': substance,
        'intype1': inType1,
        'invalue1': inValue1,
        'intype2': inType2,
        'invalue2': inValue2,
        'extra': extra
      }
      
      var retries = 0;
      var response = null;
      var doneFlag = false;
//      var logtimeS = (new Date()).getTime();
      while (retries < RETRIES_MAX){
        retries += 1;
        Logger.log(this._UrlCombine(this._getBaseUrl() + "/propsi",payload));
        try{
          response = UrlFetchApp.fetch(
            this._UrlCombine(
              this._getBaseUrl() + "/flash",
              payload
            )
          );
          if (response.getResponseCode() === 200){
            doneFlag = true;
            break;
          }
        }
        catch(err){
          Logger.log(retries + " times Fetch Error for " + payload);
        }
      }
//      Logger.log((new Date()).getTime() - logtimeS);
      if (!doneFlag){
        throw new Error("Target Server can not be access, edit your BASEURL list.");
        return null;
      }
      var data = JSON.parse(response)['result'];
      var res = [[""]]
      if (data){
        if (data['error']){
          if (data['message']) throw new Error("Error occur: " + data['message']);
          if (data['substance']) throw new Error('Not supported substance, check SUBSTANCE_REF for supported substances');
          return null;
        }
        
        // to result
        function _toOutList(result, data_dict, column){
          const IN2OUT = {
            "IN":"Input",
            "VAPFRAC":"Vapor",
            "LIQFRAC":"Liquid"
                         };
          const OUT = ["M", "D", "H", "S", "V", "Z"];
          result[0].push(IN2OUT[column]);
          var i = 0, j;
          while (i < data_dict["components"].length){
            result[i + 1].push(data_dict[column]["Fraction"][i]);
            i += 1;
          }
          i += 1;
          for (j in OUT){
            result[i].push(data_dict[column][OUT[j]]);
            i += 1;
          }
          if (column == "IN"){
            const state = ["T", "P", "Q"];
            for (j in state){
              result[i].push(data_dict[state[j]]);
              i += 1;
            }
          }
          return result
        }
        
        for (i in data["components"]){
          res.push([data["components"][i]]);
        }
        res.push(["MoleMass"]);
        res.push(["Density"]);
        res.push(["Enthalpy"]);
        res.push(["Entropy"]);
        res.push(["Visicosity"]);
        res.push(["CompressFactor"]);
        res.push(["Temperature"]);
        res.push(["Pressure"]);
        res.push(["VaporFraction"]);
        
        //
        res = _toOutList(res, data, "IN");
        
        if ("VAPFRAC" in data){
          res = _toOutList(res, data, "VAPFRAC");
        }
        if ("LIQFRAC" in data){
          res = _toOutList(res, data, "LIQFRAC");
        }
        
        if (data['warning']){
          res[0].push('warning');
          res[1].push(data['message']);
        }
      }
      return res;
    }
  }
  root['ALprop'] = ALprop();
})(this);

(function(root){
  function Util(){
    if (!(this instanceof Util)){
      return new Util();
    }
  };
  Util.prototype = {
    "isSuperSet": function(set, subset) {
      for (key in subset) {
        if (!(set.indexOf(subset[key]) > -1)) {
          return false;
        }
      }
      return true;
    },
    
    "toSet": function(array){
      res = [];
      for (key in array){
        if (!(res.indexOf(array[key]) > -1)){
          res.push(array[key]);
        }
      };
      return res;
    },
    
    "getOverlap2D": function(arrays, extend1mode){
      
    // mode 如果一个数组的x或者y是长度是1的时候是否进行扩展
      var res = [];
      var x = [], y = [], i;
      // 获取各个子数组的长和宽
      for (i in arrays){
        if (arrays[i].map && arrays[i][0].map){
          x.push(arrays[i][0].length)
          y.push(arrays[i].length)
        } else {
          y.push(1)
          if (arrays[i].map){
            x.push(arrays[i].length)
            arrays[i] = [arrays[i]]
          } else {
            x.push(1)
            arrays[i] = [[arrays[i]]]
          }
        }
      }
      // 对长宽数组进行排序 小->大
      x.sort()
      y.sort()
      
      // 去重
      x = this.toSet(x)
      y = this.toSet(y)
      // 完成后，进一步检查输入错误
      // 除去没有数据的状况
      if (x[0] < 1 || y[0] < 1){
        return []
      }
      //按照是否使用1扩展来决定输出数组的长度
      if ((x[0] == 1 || y[0] == 1) && extend1mode){
        x = x[0] == 1 && x[1] ? x[1] : x[0];
        y = y[0] == 1 && y[1] ? y[1] : y[0];
      } else {
        x = x[0];
        y = y[0];
      }
      // 构造输出数组res
      var temp = [], tempx = [], iy;
      for (i = 0; i < arrays.length; i++){
        for (iy = 0; iy < y; iy++){
          if (iy >= arrays[i].length){
            temp.push(temp[iy - 1])
          } else {
            tempx = arrays[i][iy]
            while (tempx.length < x){
              tempx = tempx.concat(tempx)
            }
            tempx = tempx.slice(0,x)
            temp[iy] = tempx
          }
        }
        res.push(temp)
        temp = []
      }
      return res;
    }
  }
  root['Util'] = Util();
})(this);


//=======================================================================================================================================
// W R A P P E R
//=======================================================================================================================================
/**
 * get substance properties calculation from CoolProp Server
 *
 * @param {H} OutputType - Out put type of the calculation, get full list on HaProp_NameOfTheProperties.
 * @param {3} C1 - quadratic coefficient
 * @param {6} C2 - primary coefficient
 * @param {0} mode - optional, defualt(0) to return first root, !=0 to return an array of roots: >0 for vertically; <0 for horizontally
 * @return {number|Array} depencing on mode, either a root or the array of 4 numbers: 3 roots and the discriminant.
 * @customfunction
 */


/**
 * get substance properties calculation from CoolProp backend.
 * 
 * @param {"Z"} outputtype - Out put type of the calculation, check PropSI_NameOfTheProperties for Types.
 * @param {"H2"} substance - Calculation substances code, get full list on PropSI_NameOfSubstances.
 * @param {"T"} type1 - Code for 1st input properties, check PropSI_NameOfTheProperties for Types.
 * @param {273.15} value1 - value of 1st input properties, check PropSI_NameOfTheProperties for Units.
 * @param {"P"} type2 - Code for 2nd input properties, check PropSI_NameOfTheProperties for types.
 * @param {101325} value2 - value of 2nd input properties, check PropSI_NameOfTheProperties for Units.
 * @param {REFPROP} backend - backend, available in [REFPROP, CP, SRK, PR].
 * @param {false} suppress warning, True to suppress server site calculation warning.
 * @param {false} keys - *default=False for single output, True for multi output except MIX out* if -True- return 2 rows of content, 1st row is output type.
 *
 * @customfunction
 */
function properties(outputtype, substance, type1, value1, type2, value2, backend, suppress, keys){
  var res = ALprop.propsi(substance, outputtype, type1, value1, type2, value2, ["SRK", "PR", "CP"].indexOf(backend) < 0? "REFPROP": backend)

  Logger.log(res);
  suppress = !!suppress;


  if (res[0].length )
  if (!keys){
    if (!suppress) {
      return [res[1]];
    } else {
      return res[1][0];
    }
  } else {
    if (!suppress) {
      return res;
    } else {
      return [[res[0]],[res[1]]]
    }
  }  
}

/**
 * get substance density calculation using REFPROP backend from CoolProp Server
 *
 * @param {"water"} substance - Calculation substances code, get full list on PropSI_NameOfSubstances.
 * @param {"T"} type1 - Code for 1st input properties, check PropSI_NameOfTheProperties for Types.
 * @param {273.15} value1 - value of 1st input properties, check PropSI_NameOfTheProperties for Units.
 * @param {"P"} type2 - Code for 2nd input properties, check PropSI_NameOfTheProperties for types.
 * @param {101325} value2 - value of 2nd input properties, check PropSI_NameOfTheProperties for Units.
 * @return {value} return density in kg/cum.
 * @customfunction
 */
function density(substance, type1, value1, type2, value2, no_REFPROP){
  if (!substance.map && !type1.map && !value1.map && !type2.map && !value2.map){
    return ALprop.propsi(substance,"D", type1, value1, type2, value2, !no_REFPROP)[1][0];
  }
  
  var templist = Util.getOverlap2D([substance,
                                    type1,
                                    value1,
                                    type2,
                                    value2
                                   ],
                                   true);
  var x, y;
  var res = [];
  var x_res, y_res;
  for(y = 0; y < templist[0].length; y++){
    y_res = [];
    for(x = 0; x < templist[0][0].length; x++){
      try{
        x_res = ALprop.propsi(templist[0][y][x],
                              'D', 
                              templist[1][y][x], 
                              templist[2][y][x], 
                              templist[3][y][x], 
                              templist[4][y][x], 
                              !no_REFPROP? "REFPROP": "CP")[1][0];
        y_res.push(x_res);
      }catch(e){
        y_res.push("[Error]" + e["message"]);
      }
    }
    res.push(y_res);
  }
  return res
}

/**
 * get substance compress factor calculation using REFPROP backend from CoolProp Server
 *
 * @param {"water"} substance - Calculation substances code, get full list on PropSI_NameOfSubstances.
 * @param {"T"} type1 - Code for 1st input properties, check PropSI_NameOfTheProperties for Types.
 * @param {273.15} value1 - value of 1st input properties, check PropSI_NameOfTheProperties for Units.
 * @param {"P"} type2 - Code for 2nd input properties, check PropSI_NameOfTheProperties for types.
 * @param {101325} value2 - value of 2nd input properties, check PropSI_NameOfTheProperties for Units.
 * @return {value} return compress factor.
 * @customfunction
 */
function Z(substance, type1, value1, type2, value2, no_REFPROP){
  return ALprop.propsi(substance, 'Z', type1, value1, type2, value2, !no_REFPROP? "REFPROP": "CP")[1][0];
}

/**
 * get flash calculation using REFPROP backend from CoolProp Server
 *
 * @param {"[O2:21, N2:78, Argon:1]"} substance - Calculation substances code, get full list on PropSI_NameOfSubstances.
 * @param {"Q"} type1 - Code for 1st input properties, check PropSI_NameOfTheProperties for Types.
 * @param {0.3} value1 - value of 1st input properties, check PropSI_NameOfTheProperties for Units.
 * @param {"P"} type2 - Code for 2nd input properties, check PropSI_NameOfTheProperties for types.
 * @param {101325} value2 - value of 2nd input properties, check PropSI_NameOfTheProperties for Units.
 * @param {REFPROP} backend - backend, available in [REFPROP, CP].
 * @customfunction
 */
function mixture_flash(substance, type1, value1, type2, value2, no_REFPROP){
  var res = ALprop.flash(substance, type1, value1, type2, value2, !no_REFPROP? "REFPROP": "CP");
  return res
}


//====================================================================================================
//====================================================================================================
/**
 * Calculating the properties of wet air.
 *
 * @param {"W"} outType - Output code of the calculation.
 * @param {"T"} type1 - Code for 1st input properties, check PropSI_NameOfTheProperties for Types.
 * @param {273.15} value1 - value of 1st input properties, check PropSI_NameOfTheProperties for Units.
 * @param {"P"} type2 - Code for 2nd input properties, check PropSI_NameOfTheProperties for types.
 * @param {101325} value2 - value of 2nd input properties, check PropSI_NameOfTheProperties for Units.
 * @param {"R"} type3 - Code for 3rd input properties, check PropSI_NameOfTheProperties for types.
 * @param {0.3} value3 - value of 3rd input properties, check PropSI_NameOfTheProperties for Units.
 * @return {value} return value of the output type.
 * @customfunction
 */
function humiAir(outType, type1, value1, type2, value2, type3, value3){
  var data = ALprop.haprop(outType, type1, value1, type2, value2, type3, value3);
  return data[1][data[0].indexOf(outType)];
}

/**
 * Multiplies an input value by 2.
 * @param {number} input The number to double.
 * @return The input multiplied by 2.
 * @customfunction
*/
function rs(){
  return [['T', 'VAPFRAC'], [84.87080768127659, [0.6861548000076236, 0.29558516609053737, 0.018260033901839057]]]
}


function test(){
//  ALprop.flash("[O2:21, N2:78, AR:1]", "Q", 0.3, "P", 101325, "REFPROP");
  Logger.log(properties("T,V,Z", "[N2:46.0919148480653,O2:51.604049876984,AR:2.30403527495069]", "S", 5555, "P", 123325))
  Logger.log(properties("H,Z,Q", "[N2:46.0919148480653,O2:51.604049876984,AR:2.30403527495069]", "Q", 0.3, "P", 123325))
  Logger.log(properties("VAPFRAC, T", "[N2:46.0919148480653,O2:51.604049876984,AR:2.30403527495069]", "Q", 0.3, "P", 123325))
  // Logger.log(Array.isArray([]))
  // Logger.log([].length)
    // var PROPSI = ["DELTA", "DMOLAR", "D", "HMOLAR", "H", "P", "Q", "SMOLAR", "S", "TAU", "T", "UMOLAR", "U", "ACENTRIC", "ALPHA0", "ALPHAR", "A", "BVIRIAL", "CONDUCTIVITY", "CP0MASS", "CP0MOLAR", "CPMOLAR", "CVIRIAL", "CVMASS", "CVMOLAR", "CP", "DALPHA0_DDELTA_CONSTTAU", "DALPHA0_DTAU_CONSTDELTA", "DALPHAR_DDELTA_CONSTTAU", "DALPHAR_DTAU_CONSTDELTA", "DBVIRIAL_DT", "DCVIRIAL_DT", "DIPOLE_MOMENT", "FH", "FRACTION_MAX", "FRACTION_MIN", "FUNDAMENTAL_DERIVATIVE_OF_GAS_DYNAMICS", "GAS_CONSTANT", "GMOLAR", "GWP100", "GWP20", "GWP500", "G", "HELMHOLTZMASS", "HELMHOLTZMOLAR", "HH", "ISBRCOEFF", "ISTHCOEFF", "I", "M", "ODP", "PCRIT", "PHASE", "PH", "PIP", "PMAX", "PMIN", "PRANDTL", "PTRIPLE", "P_REDUCING", "RHOCRIT", "RHOMASS_REDUCING", "RHOMOLAR_CRITICAL", "RHOMOLAR_REDUCING", "SMOLAR_RESIDUAL", "TCRIT", "TMAX", "TMIN", "TTRIPLE", "T_FREEZE", "T_REDUCING", "V", "Z"];

}
from typing import TypedDict
from typing import List


class LookupTables(TypedDict):
    file_name: str
    columns: List[str]


deviceclass: LookupTables = {
    "file_name": "DeviceClass.csv",
    "columns": [
        "deviceclassid",
        "balancegroupid",
        "deviceclasstype",
        "tvmtarversiongroupid",
        "tvmapltarversiongroupid",
        "tvmtechversiongroupid",
        "tvmswversiongroupid",
        "description",
        "testflag",
        "usernew",
        "timenew",
        "userchange",
        "timechange",
        "typeoftariffdownloaddata",
        "parametergroupid",
    ],
}

event: LookupTables = {
    "file_name": "Event.csv",
    "columns": [
        "eventcode",
        "eventdesc",
        "eventtxt",
        "eventgroupref",
        "display",
        "logging",
        "alarm",
        "sendevent",
        "usernew",
        "timenew",
        "userchange",
        "timechange",
    ],
}

eventgroup: LookupTables = {
    "file_name": "EventGroup.csv",
    "columns": [
        "eventgroupref",
        "eventgroupdesc",
        "usernew",
        "timenew",
        "userchange",
        "timechange",
    ],
}

holiday: LookupTables = {
    "file_name": "Holiday.csv",
    "columns": [
        "versionid",
        "datehour",
        "holidayclass",
        "description",
        "usernew",
        "timenew",
        "userchange",
        "timechange",
    ],
}

mbta_weekend_service: LookupTables = {
    "file_name": "MBTA_Weekend_Service.csv",
    "columns": [
        "servicehour",
        "servicedesc",
        "servicetype",
        "dateinserted",
    ],
}

routes: LookupTables = {
    "file_name": "Routes.csv",
    "columns": [
        "routeid",
        "description",
        "versionid",
        "multimediagroupid",
        "usernew",
        "timenew",
        "userchange",
        "timechange",
    ],
}

tariffversions: LookupTables = {
    "file_name": "TariffVersions.csv",
    "columns": [
        "versionid",
        "validitystarttime",
        "validityendtime",
        "railroadid",
        "description",
        "status",
        "theovertakerflag",
        "usernew",
        "timenew",
        "userchange",
        "timechange",
        "type",
    ],
}

tickettype: LookupTables = {
    "file_name": "TicketType.csv",
    "columns": [
        "versionid",
        "tickettypeid",
        "summary",
        "type",
        "amount",
        "balamt1",
        "balamt2",
        "farecalculationruleid",
        "multimediagroupid",
        "statetaxid",
        "sendonlevt",
        "svcproviderid",
        "validityid",
        "genderinput",
        "description",
        "param1",
        "param2",
        "param3",
        "param4",
        "param5",
        "param6",
        "param7",
        "param8",
        "param9",
        "param10",
        "usernew",
        "timenew",
        "userchange",
        "timechange",
        "ticketmembergroupid",
        "externalid",
    ],
}

tvmstation: LookupTables = {
    "file_name": "TVMStation.csv",
    "columns": [
        "stationid",
        "nameshort",
        "namelong",
        "name",
        "town",
        "tariffproperty",
        "tariffzone",
        "usernew",
        "timenew",
        "userchange",
        "timechange",
        "companyid",
        "graphickey",
        "stationtype",
        "externalid",
    ],
}

tvmtable: LookupTables = {
    "file_name": "TVMTable.csv",
    "columns": [
        "deviceclassid",
        "deviceid",
        "balancegroupid",
        "tvmabbreviation",
        "tvmlocation1",
        "tvmlocation2",
        "tvmpostalcode",
        "tvmgroupref",
        "locationid",
        "tvmtariffzoneid",
        "tvmtarversiongroupid",
        "tvmapltarversiongroupid",
        "tvmtechversiongroupid",
        "tvmswversiongroupid",
        "tvminstanceid",
        "tvmnetaddr",
        "tvmnetsubaddr",
        "tvmrouteraddr",
        "companyid",
        "tvmlicense1",
        "tvmlicense2",
        "tvmphonenumber",
        "tvmfepgroupref",
        "tvmnetconfgroupref",
        "tvmnetmode",
        "graphickey",
        "defaultdestgroupid",
        "routeid",
        "defaultstartgroupid",
        "versionid",
        "bankcode",
        "bankaccount",
        "multimediagroupid",
        "reserved4",
        "reserved5",
        "reserved6",
        "reserved7",
        "reserved8",
        "reserved9",
        "reserved3",
        "reserved2",
        "reserved1",
        "serialno",
        "fieldstate",
        "usernew",
        "timenew",
        "userchange",
        "timechange",
        "parametergroupid",
    ],
}

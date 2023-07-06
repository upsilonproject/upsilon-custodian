package reports

import (
	"fmt"
	db "github.com/upsilonproject/upsilon-custodian/internal/db"
	log "github.com/sirupsen/logrus"
	"database/sql"
	"github.com/doug-martin/goqu/v9"
	pb "github.com/upsilonproject/upsilon-custodian/gen/amqpproto"
)

func Get(includeGood bool) *pb.ReportResponse {
	res := getFromDatabase(includeGood)

	ret := newReport("id", "service", "node", "karma", "lastUpdated")
	ret.Columns[4].Type = "timestamp"

	for res.Next() {
		var id int;
		var identifier string;
		var node string;
		var karma string;
		var lastUpdated string;

		err := res.Scan(&id, &identifier, &node, &karma, &lastUpdated)

		if err != nil {
			log.Errorf("scanf: %s", err)
		}

		row := &pb.ReportRow {
			Cells: map[string]string {
				"id": fmt.Sprintf("%v", id),
				"service": identifier,
				"node": node,
				"karma": karma,
				"lastUpdated": lastUpdated,
			},
		}

		ret.Rows = append(ret.Rows, row)
	}

	res.Close()

	return ret;
}

func newReport(headers ...string) *pb.ReportResponse {
	ret := &pb.ReportResponse{
		Rows: []*pb.ReportRow {},
		Columns: []*pb.ReportColumn {},
	}

	for _, header := range headers {
		ret.Columns = append(ret.Columns, &pb.ReportColumn {
			Type: "string",
			Header: header,
		})

	}

	return ret
}

func getFromDatabase(includeGood bool) *sql.Rows {
	sql := reportRequestToSql(includeGood)

	dbhandle := db.GetDb()

	res, err := dbhandle.Query(sql);

	if err != nil {
		log.Warnf("Query err: %v", err)
	}

	return res;
}

func reportRequestToSql(includeGood bool) string {
	//"SELECT id, identifier as service, node, karma, lastUpdated FROM services ORDER BY karma");

	builder := db.GetGoqu().From("services").Select("id", goqu.C("identifier").As("serivce"), "node", "karma", "lastUpdated");

	if !includeGood {
		builder = builder.Where(goqu.C("karma").Neq("good"))
	}

	sql, _, err := builder.ToSQL();

	if err != nil {
		log.Errorf("report sql prep error: %v", err)
	} else {
		log.Debugf("report sql: %s", sql);
	}

	return sql
}


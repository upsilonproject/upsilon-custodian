package amqp;

import (
	"database/sql"
	_ "github.com/go-sql-driver/mysql"
	"github.com/doug-martin/goqu/v9"
	_ "github.com/doug-martin/goqu/v9/dialect/mysql"

	log "github.com/sirupsen/logrus"

	"sync"
)

var db *sql.DB;
var dbLock sync.Mutex;


func GetDb() *sql.DB {
	dbLock.Lock();

	if db == nil {
		var err error;

		db, err = sql.Open("mysql", "upsilon:upsilon@tcp(upsilon:3306)/upsilon")

		if err != nil {
			log.Errorf("%v", err)
		}
	}

	dbLock.Unlock();

	return db;
}

func GetGoqu() *goqu.Database {
	return goqu.New("mysql", db)
}

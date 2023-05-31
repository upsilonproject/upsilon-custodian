package snapshot

import (
	"time"
	"os"
	"io"
	log "github.com/sirupsen/logrus"
	"gopkg.in/yaml.v2"
	"strings"
	"net/http"
)

type Snapshot struct {
	Timestamp string
	Metrics []Metric
}

type Metric struct {
	Name string
	Value float64
}

func RunForever() {
	host := os.Getenv("SNAPSHOT_HOST")

	if host == "" {
		log.Warnf("No SNAPSHOT_HOST specified")
		return
	}

	for {
		log.Infof("Running Snapshot")
		run(host)
		time.Sleep(60 * time.Second)
	}
}

func getSnapshot() *Snapshot {
	ret := &Snapshot {
		Timestamp: time.Now().Format(time.RFC850),
	}

	return ret
}

func run(host string) {
	yamlData, err := yaml.Marshal(getSnapshot())

	if err != nil {
		log.Errorf("Snapshot yaml marshal failure: %v", err)
		return
	}

	resp, err := http.Post(host, "text/yaml", strings.NewReader(string(yamlData)))

	if err != nil {
		log.Errorf("Snapshot failed. %v", err)
		return
	}
	
	txt, err := io.ReadAll(resp.Body)

	if err != nil {
		log.Errorf("Snapshot read failed: %v", err)
		return
	}

	log.Infof("Snapshot status: %v", string(txt))
}

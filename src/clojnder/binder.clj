(ns clojnder.binder
  (:gen-class)
  (:require [clojnder.clay :as clay]))

(defn -main [& args]
  (clay/start-server! {:args args
                       :env-port-var "CLAY_BINDER_PORT"
                       :default-port 8080
                       :base-source-path (or (System/getenv "CLAY_BASE_PATH") ".")
                       :base-target-path (or (System/getenv "CLAY_TARGET_PATH") ".clay")
                       :starter-doc (or (System/getenv "CLAY_STARTER_DOC") "notebooks/examples.clj")
                       :url-prefix (System/getenv "CLAY_URL_PREFIX")}))

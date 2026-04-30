(ns clojnder.check
  (:gen-class)
  (:require [clojnder.clay :as clay]))

(defn -main [& _args]
  (let [starter-doc (or (System/getenv "CLAY_STARTER_DOC") "notebooks/examples.clj")]
    (try
      (clay/validate-starter-doc! starter-doc)
      (println (str "Starter document is valid: " starter-doc))
      (System/exit 0)
      (catch Throwable t
        (binding [*out* *err*]
          (println (str "Starter document is invalid: " starter-doc))
          (println (.getMessage t)))
        (System/exit 1)))))

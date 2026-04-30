(ns clojnder.render
  (:gen-class)
  (:require [clojnder.clay :as clay]))

(defn -main [& _args]
  (let [base-source-path (or (System/getenv "CLAY_BASE_PATH") ".")
        base-target-path (or (System/getenv "CLAY_TARGET_PATH") ".clay")
        starter-doc (or (System/getenv "CLAY_STARTER_DOC") "notebooks/examples.clj")]
    (try
      (clay/render-starter-doc! {:base-source-path base-source-path
                                 :base-target-path base-target-path
                                 :starter-doc starter-doc})
      (println (str "Rendered starter document: " starter-doc))
      (System/exit 0)
      (catch Throwable t
        (binding [*out* *err*]
          (println (str "Render failed for starter document: " starter-doc))
          (println (.getMessage t)))
        (System/exit 1)))))

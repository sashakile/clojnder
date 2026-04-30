(ns clojnder.render
  (:gen-class)
  (:require [clojnder.clay :as clay]))

(defn- parse-file-arg [args]
  (some (fn [[flag value]]
          (when (= flag "--file") value))
        (partition 2 1 args)))

(defn -main [& args]
  (let [base-source-path (or (System/getenv "CLAY_BASE_PATH") ".")
        base-target-path (or (System/getenv "CLAY_TARGET_PATH") ".clay")
        source-path (or (parse-file-arg args)
                        (System/getenv "CLAY_STARTER_DOC")
                        "notebooks/examples.clj")]
    (try
      (clay/safe-render-file! {:base-source-path base-source-path
                                :base-target-path base-target-path
                                :source-path source-path})
      (println (str "Rendered: " source-path))
      (System/exit 0)
      (catch Throwable t
        (binding [*out* *err*]
          (println (str "Render failed: " source-path))
          (println (.getMessage t)))
        (System/exit 1)))))

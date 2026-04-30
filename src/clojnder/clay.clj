(ns clojnder.clay
  (:require [clojure.java.io :as io]
            [clojure.string :as str])
  (:refer-clojure :exclude [run!]))

(defn parse-port
  ([args default-port]
   (or (some (fn [[flag value]]
               (when (= flag "--port")
                 (Integer/parseInt value)))
             (partition 2 1 args))
       default-port))
  ([default-port]
   default-port))

(defn resolve-clay-start! []
  (or (try
        (requiring-resolve 'scicloj.clay.v2.api/start!)
        (catch Throwable _ nil))
      (try
        (requiring-resolve 'scicloj.clay.v2.api/serve!)
        (catch Throwable _ nil))
      (throw (ex-info "Could not resolve a Clay server entrypoint" {}))))

(defn- rewrite-html-for-prefix [html prefix]
  (-> html
      (str/replace "fetch('/" (str "fetch('" prefix "/"))
      (str/replace "src=\"/" (str "src=\"" prefix "/"))
      (str/replace "href=\"/" (str "href=\"" prefix "/"))
      (str/replace "location.assign('http://localhost:'+clay_port);"
                   (str "location.assign(window.location.origin + '" prefix "/');"))
      (str/replace "new WebSocket('ws://localhost:'+clay_port);"
                   (str "new WebSocket((window.location.protocol === 'https:' ? 'wss://' : 'ws://') + window.location.host + '" prefix "/');"))))

(defn install-proxy-prefix-patch! [prefix]
  (when (seq prefix)
    (let [wrap-html-var (requiring-resolve 'scicloj.clay.v2.server/wrap-html)
          original @wrap-html-var]
      (alter-var-root wrap-html-var
                      (fn [_]
                        (fn [html state]
                          (-> (original html state)
                              (rewrite-html-for-prefix prefix))))))))

(defn- starter-doc-spec [base-source-path starter-doc base-target-path]
  (let [candidate (some-> starter-doc io/file)]
    (when (and candidate (.exists candidate))
      {:base-source-path base-source-path
       :base-target-path base-target-path
       :source-path starter-doc
       :show true
       :browse false
       :browse? false
       :live-reload true
       :watch-dirs [base-source-path]})))

(defn starter-doc-path [starter-doc]
  (some-> starter-doc io/file .getPath))

(defn validate-starter-doc! [starter-doc]
  (when starter-doc
    (let [path (starter-doc-path starter-doc)
          file (some-> path io/file)]
      (when (and file (.exists file))
        (with-open [rdr (java.io.PushbackReader. (io/reader file))]
          (loop []
            (let [form (read rdr false ::eof)]
              (when-not (= form ::eof)
                (recur)))))))
    true))

(defn render-starter-doc! [{:keys [base-source-path starter-doc base-target-path]}]
  (if-let [spec (starter-doc-spec base-source-path starter-doc base-target-path)]
    (do
      (println (str "Rendering starter document " starter-doc))
      (validate-starter-doc! starter-doc)
      ((requiring-resolve 'scicloj.clay.v2.api/make!) spec)
      :rendered)
    (do
      (println "No starter document configured; Clay will show its default welcome page.")
      :missing)))

(defn safe-render-starter-doc! [opts]
  (try
    (render-starter-doc! opts)
    (catch Throwable t
      (println (str "Starter document render failed: " (.getMessage t)))
      (println "Clay server is still running; fix the file and refresh/restart as needed.")
      :failed)))

(defn render-file! [{:keys [base-source-path source-path base-target-path]}]
  (println (str "Rendering " source-path))
  ((requiring-resolve 'scicloj.clay.v2.api/make!)
   {:base-source-path base-source-path
    :base-target-path base-target-path
    :source-path source-path
    :show true
    :browse false
    :browse? false
    :live-reload false})
  :rendered)

(defn safe-render-file! [opts]
  (try
    (render-file! opts)
    (catch Throwable t
      (println (str "File render failed: " (.getMessage t)))
      :failed)))

(defn start-server! [{:keys [args env-port-var default-port base-source-path starter-doc base-target-path url-prefix]
                      :or {args []
                           default-port 1971
                           base-source-path "."
                           base-target-path ".clay"}
                      :as opts}]
  (let [port (or (parse-port args nil)
                 (some-> env-port-var System/getenv Integer/parseInt)
                 default-port)
        start! (resolve-clay-start!)
        server-opts {:base-source-path base-source-path
                     :base-target-path base-target-path
                     :port port
                     :browse false
                     :browse? false}]
    (println (str "Starting Clay on port " port " with base path " base-source-path))
    (install-proxy-prefix-patch! url-prefix)
    (start! server-opts)
    (safe-render-starter-doc! opts)
    (println "Clay is running. Keeping the process alive.")
    @(promise)))

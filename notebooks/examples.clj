^{:kind/hiccup true :kindly/hide-code true}
[:div
 [:h1 "Clay examples"]
 [:p "A small starter notebook inspired by the Clay book examples."]
 [:p "This page is served by Clay through the local container or Binder proxy."]
 [:p "Try editing " [:code "notebooks/examples.clj"] " and refreshing."]]

^{:kind/hiccup true}
[:h2 "A table"]

[{:name "Ada" :role "engineer" :score 98}
 {:name "Grace" :role "scientist" :score 95}
 {:name "Edsger" :role "researcher" :score 99}]

^{:kind/hiccup true}
[:h2 "Simple hiccup"]

^{:kind/hiccup true}
[:ul
 [:li "Clay can render hiccup"]
 [:li "Sequential data often renders nicely as a table"]
 [:li "Charts can be expressed as data too"]]

^{:kind/hiccup true}
[:h2 "A Vega-Lite chart"]

^{:kind/vega-lite true}
{:data {:values [{:x 1 :y 2}
                 {:x 2 :y 3}
                 {:x 3 :y 5}
                 {:x 4 :y 8}]}
 :mark {:type "line" :point true}
 :encoding {:x {:field :x :type "quantitative"}
            :y {:field :y :type "quantitative"}}}

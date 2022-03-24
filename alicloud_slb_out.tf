resource "alicloud_slb_server_group" "crm" {

  name             = "http-80"

  load_balancer_id = var.ali_slb_id["crm"]

  servers {

    server_ids     = ["i-2ze60jo4cnn5ipzea6kh"]

    weight         = 100

    port           = 80

  }

}
resource "alicloud_slb_server_group" "kong" {

  name             = "http-80"

  load_balancer_id = var.ali_slb_id["kong"]

  servers {

    server_ids     = ["i-2ze2ahofeot4tnfbde4s"]

    weight         = 100

    port           = 80

  }

}
resource "alicloud_slb_server_group" "www" {

  name             = "http-80"

  load_balancer_id = var.ali_slb_id["www"]

  servers {

    server_ids     = ["i-2ze5eib0jy8o5d9762b0", "i-2ze7jkui6izg66r67q7k"]

    weight         = 100

    port           = 80

  }

}
resource "alicloud_slb_server_group" "crm" {

  name             = "http-80"

  load_balancer_id = var.ali_slb_id["crm"]

  servers {

    server_ids     = ["i-2ze60jo4cnn5ipzea6kh"]

    weight         = 100

    port           = 80

  }

}
resource "alicloud_slb_server_group" "kong" {

  name             = "http-80"

  load_balancer_id = var.ali_slb_id["kong"]

  servers {

    server_ids     = ["i-2ze2ahofeot4tnfbde4s"]

    weight         = 100

    port           = 80

  }

}
resource "alicloud_slb_server_group" "www" {

  name             = "http-80"

  load_balancer_id = var.ali_slb_id["www"]

  servers {

    server_ids     = ["i-2ze5eib0jy8o5d9762b0", "i-2ze7jkui6izg66r67q7k"]

    weight         = 100

    port           = 80

  }

}
resource "alicloud_slb_server_group" "crm" {

  name             = "http-80"

  load_balancer_id = var.ali_slb_id["crm"]

  servers {

    server_ids     = ["i-2ze60jo4cnn5ipzea6kh"]

    weight         = 100

    port           = 80

  }

}
resource "alicloud_slb_server_group" "kong" {

  name             = "http-80"

  load_balancer_id = var.ali_slb_id["kong"]

  servers {

    server_ids     = ["i-2ze2ahofeot4tnfbde4s"]

    weight         = 100

    port           = 80

  }

}
resource "alicloud_slb_server_group" "www" {

  name             = "http-80"

  load_balancer_id = var.ali_slb_id["www"]

  servers {

    server_ids     = ["i-2ze5eib0jy8o5d9762b0", "i-2ze7jkui6izg66r67q7k"]

    weight         = 100

    port           = 80

  }

}
